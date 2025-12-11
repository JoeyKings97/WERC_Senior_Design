# PLC Tag Map (fill with your addresses)

Proposed Modbus mapping (adjust to your PLC program):

- Input registers 0-3: humidity (x10), temperature (x10), airflow (x10), condensate_rate (x10)
- Coil 1: pump enable (written by backend when control is enabled)

Document ladder/ST implementation details here:

- Safety interlocks stay on PLC (low sump level, overloads, emergency stop)
- Backend should only request/command through defined coils/registers
