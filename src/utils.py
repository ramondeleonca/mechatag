import os

def get_pi_model():
    with open('/sys/firmware/devicetree/base/model') as f:
        return f.read()

def is_pi():
    if os.path.exists('/sys/firmware/devicetree/base/model'):
        return 'pi' in get_pi_model().lower()
    return False