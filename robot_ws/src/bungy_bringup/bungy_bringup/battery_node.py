#!/usr/bin/env python3
"""Battery voltage and current from an INA219 (Adafruit breakout, 0.1 ohm shunt) on I2C.

Publishes sensor_msgs/BatteryState on /bungy/battery. Only reads registers (no configuration is
written, so the chip keeps its power-on defaults: 32 V range, +-320 mV shunt range -> up to 3.2 A):

  shunt voltage register 0x01: signed, 10 uV per bit  -> current = V_shunt / shunt_ohm
  bus voltage register   0x02: bits 15..3, 4 mV per bit

Sign convention of BatteryState: current is negative while discharging.
The charge percentage is estimated from the voltage per cell with a resting Li-ion curve; under
load the voltage sags, so the estimate reads low while the robot drives.
"""
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from smbus import SMBus

# resting voltage per cell (NMC/NCA Li-ion) -> fraction of charge
CURVE = [(3.00, 0.00), (3.30, 0.02), (3.40, 0.06), (3.50, 0.12), (3.60, 0.22), (3.70, 0.35),
         (3.80, 0.50), (3.90, 0.65), (4.00, 0.80), (4.10, 0.90), (4.20, 1.00)]


def fraction(cell_voltage):
    if cell_voltage <= CURVE[0][0]:
        return 0.0
    for (v0, f0), (v1, f1) in zip(CURVE, CURVE[1:]):
        if cell_voltage <= v1:
            return f0 + (f1 - f0) * (cell_voltage - v0) / (v1 - v0)
    return 1.0


class BatteryNode(Node):
    def __init__(self):
        super().__init__('battery')
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('address', 0x40)
        self.declare_parameter('shunt_ohm', 0.1)
        self.declare_parameter('cells', 3)
        self.declare_parameter('design_capacity_ah', 5.2)
        self.declare_parameter('rate_hz', 2.0)
        self.declare_parameter('warn_voltage', 10.5)    # same as the driver's min_voltage_warn
        self.declare_parameter('critical_voltage', 9.6)  # same as the driver's min_voltage_stop
        g = lambda n: self.get_parameter(n).value
        self.address, self.shunt, self.cells = g('address'), g('shunt_ohm'), g('cells')
        self.capacity, self.warn, self.critical = g('design_capacity_ah'), g('warn_voltage'), g('critical_voltage')
        self.bus = SMBus(g('i2c_bus'))
        self.pub = self.create_publisher(BatteryState, '/bungy/battery', 10)
        self.errors = 0
        self.create_timer(1.0 / g('rate_hz'), self.tick)
        self.get_logger().info(f'INA219 at 0x{self.address:02x}, {self.cells} cells, shunt {self.shunt} ohm')

    def word(self, reg):
        raw = self.bus.read_word_data(self.address, reg)   # SMBus is little endian, the chip big endian
        return ((raw & 0xFF) << 8) | (raw >> 8)

    def tick(self):
        try:
            shunt_raw = self.word(0x01)
            bus_raw = self.word(0x02)
        except OSError as e:
            self.errors += 1
            self.get_logger().warn(f'INA219 read failed ({e}), {self.errors} so far', throttle_duration_sec=30.0)
            return
        if shunt_raw >= 0x8000:
            shunt_raw -= 0x10000
        voltage = (bus_raw >> 3) * 0.004
        current = shunt_raw * 10e-6 / self.shunt       # A, positive = the load draws current

        msg = BatteryState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.voltage = voltage
        msg.current = -current                          # negative while discharging
        msg.charge = float('nan')
        msg.capacity = float('nan')
        msg.design_capacity = self.capacity
        msg.percentage = fraction(voltage / self.cells)
        msg.power_supply_status = (BatteryState.POWER_SUPPLY_STATUS_DISCHARGING if current > 0.05
                                   else BatteryState.POWER_SUPPLY_STATUS_UNKNOWN)
        msg.power_supply_health = BatteryState.POWER_SUPPLY_HEALTH_GOOD
        msg.power_supply_technology = BatteryState.POWER_SUPPLY_TECHNOLOGY_LION
        msg.present = voltage > 1.0
        self.pub.publish(msg)

        if voltage < self.critical:
            self.get_logger().error(f'battery CRITICAL: {voltage:.2f} V', throttle_duration_sec=10.0)
        elif voltage < self.warn:
            self.get_logger().warn(f'battery low: {voltage:.2f} V', throttle_duration_sec=30.0)


def main():
    rclpy.init()
    node = BatteryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
