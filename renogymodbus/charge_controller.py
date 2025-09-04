import minimalmodbus
import serial

from renogymodbus.retriable_instrument import RetriableInstrument


class RenogyChargeController(RetriableInstrument):
    """Instrument class for Renogy Charge Controllers.

    Args:
        * portname (str): port name
        * slaveaddress (int): slave address in the range 1 to 247

    """

    def __init__(self, portname, slaveaddress):
        super().__init__(portname, slaveaddress)
        self.serial.baudrate = 9600
        self.serial.bytesize = 8
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = 1
        self.serial.timeout = 1
        self.mode = minimalmodbus.MODE_RTU

        self.clear_buffers_before_each_transaction = True

    def get_controller_voltage_rating(self):
        """Controller battery/load voltage rating in volts"""
        return (self.retriable_read_register(0x0A, 0, 3, False) & 0xFF00) >> 8

    def get_controller_current_rating(self):
        """Controller current rating in amps"""
        return self.retriable_read_register(0x0A, 0, 3, False) & 0x00FF

    def get_controller_discharge_rating(self):
        """Controller discharge rating in amps"""
        return (self.retriable_read_register(0x0B, 0, 3, False) & 0xFF00) >> 8

    def get_controller_type(self):
        """Controller type"""
        return self.retriable_read_register(0x0B, 0, 3, False) & 0x00FF

    def get_controller_model(self):
        """Controller model name as a string"""
        output = bytearray()
        for reg in range(0x0C, 0x13 + 1):
            word = self.retriable_read_register(reg, 0, 3, False)
            output.append((word & 0xFF00) >> 8)
            output.append(word & 0x00FF)
        return output.decode(encoding='utf-8')

    def get_controller_software_version(self):
        """Controller software version as a tuple"""
        return (self.retriable_read_register(0x14, 0, 3, False), self.retriable_read_register(0x15, 0, 3, False))

    def get_controller_hardware_version(self):
        """Controller hardware version as a tuple"""
        return (self.retriable_read_register(0x16, 0, 3, False), self.retriable_read_register(0x17, 0, 3, False))

    def get_controller_serial_number(self):
        """Controller serial number"""
        output = bytearray()
        for reg in range(0x18, 0x19 + 1):
            word = self.retriable_read_register(reg, 0, 3, False)
            output.append((word & 0xFF00) >> 8)
            output.append(word & 0x00FF)
        return output

    def get_controller_modbus_address(self):
        """Controller Modbus address"""
        return self.retriable_read_register(0x1A, 0, 3, False)

    def get_solar_voltage(self):
        """PV array input in volts"""
        return self.retriable_read_register(0x0107, 1, 3, False)

    def get_solar_current(self):
        """PV array input in amps"""
        return self.retriable_read_register(0x0108, 2, 3, False)

    def get_solar_power(self):
        """PV array input in watts"""
        return self.retriable_read_register(0x0109, 0, 3, False)

    def get_load_voltage(self):
        """Load output in volts"""
        return self.retriable_read_register(0x0104, 1, 3, False)

    def get_load_current(self):
        """Load output in amps"""
        return self.retriable_read_register(0x0105, 2, 3, False)

    def get_load_power(self):
        """Load output in watts"""
        return self.retriable_read_register(0x0106, 0, 3, False)

    def get_battery_voltage(self):
        """Battery voltage"""
        return self.retriable_read_register(0x0101, 1, 3, False)

    def get_battery_current(self):
        """Battery charge current in amps"""
        return self.retriable_read_register(0x102, 2, 3, False)

    def get_battery_state_of_charge(self):
        """Battery state of charge"""
        return self.retriable_read_register(0x0100, 0, 3, False)

    def get_battery_temperature(self):
        """battery temperature"""
        register_value = self.retriable_read_register(0x0103, 0, 3, False)
        battery_temperature = register_value & 0b0000000001111111
        battery_temperature_sign = (register_value & 0b0000000010000000) >> 7
        battery_temperature = -battery_temperature if battery_temperature_sign == 1 else battery_temperature
        return battery_temperature

    def get_controller_temperature(self):
        """Temperature inside equipment"""
        register_value = self.retriable_read_register(0x0103, 0, 3, False)
        controller_temperature = (register_value & 0b0111111100000000) >> 8
        controller_temperature_sign = (register_value & 0b1000000000000000) >> 15
        controller_temperature = -controller_temperature if controller_temperature_sign == 1 else controller_temperature
        return controller_temperature

    # Check this, it doesn't match the defintion spreadsheet (should be max. charge power?)
    def get_maximum_solar_power_today(self):
        """Max solar power today"""
        return self.retriable_read_register(0x010F, 0, 3, False)

    # Check this, it doesn't match the defintion spreadsheet (should be max. load/discharge power?)
    def get_minimum_solar_power_today(self):
        """Min solar power today"""
        return self.retriable_read_register(0x0110, 0, 3, False)

    def get_maximum_battery_voltage_today(self):
        """Maximum solar power today"""
        return self.retriable_read_register(0x010C, 1, 3, False)

    def get_minimum_battery_voltage_today(self):
        """Minimum solar power today"""
        return self.retriable_read_register(0x010B, 1, 3, False)

    def get_maximum_charge_current_today(self):
        """Maximum charge current today"""
        return self.retriable_read_register(0x010D, 0, 3, False)

    def get_maximum_load_current_today(self):
        """Maximum load/discharge current today"""
        return self.retriable_read_register(0x010E, 0, 3, False)

    def get_charge_today(self):
        """Charge today in amp hours"""
        return self.retriable_read_register(0x111, 0, 3, False)

    def get_discharge_today(self):
        """Discharge today in amp hours"""
        return self.retriable_read_register(0x112, 0, 3, False)

    def get_charge_energy_today(self):
        """Charge energy today in watt hours"""
        return self.retriable_read_register(0x113, 0, 3, False)

    def get_discharge_energy_today(self):
        """Discharge energy today in watt hours"""
        return self.retriable_read_register(0x114, 0, 3, False)

    def get_controller_uptime(self):
        """Controller uptime in days"""
        return self.retriable_read_register(0x115, 0, 3, False)

    def get_total_battery_overcharges(self):
        """Total battery overcharges"""
        return self.retriable_read_register(0x116, 0, 3, False)

    def get_total_battery_full_charges(self):
        """Total battery full charges"""
        return self.retriable_read_register(0x117, 0, 3, False)
