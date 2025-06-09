import serial
import time

def sendTrigger(channel, duration=0.01, zero_marker='mh\x00'):
    """
    Send trigger to hardware device

    Parameters
    ----------
    channel : str
        Trigger channel (ch160-ch166)
    duration : float
        Trigger pulse duration in seconds
    zero_marker : str
        Reset signal

    Returns
    -------
    None
    """
    
    mapping = {
        'ch160': 'mh\x01',
        'ch161': 'mh\x02', 
        'ch162': 'mh\x04',
        'ch163': 'mh\x08',
        'ch164': 'mh\x10',
        'ch165': 'mh 0',
        'ch166': 'mh@0'
    }

    if channel not in mapping:
        print(f"Invalid channel: {channel}")
        return

    data = mapping[channel]

    try:
        # Send trigger twice for reliability
        ser.write(bytes(data, encoding='utf-8'))
        ser.write(bytes(data, encoding='utf-8'))

        # Pulse duration
        time.sleep(duration)

        # Reset pulse to zero
        ser.write(bytes(zero_marker, encoding='utf-8'))
        ser.write(bytes(zero_marker, encoding='utf-8'))

    except Exception as e:
        print(f"Trigger send error: {e}")
        if hasattr(ser, 'port') and ser.port:
            print('The serial port might be closed.')

# Initialize serial connection
ser = serial.Serial(baudrate=115200)

# Configure port (update path for your system)
try:
    ser.port = '/dev/cu.usbserial-XXXXX'  # Replace with actual port
    ser.open()
    print(f"Serial port opened: {ser.port}")
except Exception as e:
    print(f'Could not open serial port: {e}')

# Example usage:
# sendTrigger('ch160', duration=0.01)
# sendTrigger('ch161', duration=0.01)
