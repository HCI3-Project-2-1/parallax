import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_data(ip, port, new_coords):
    """Send normalized coordinates to Godot via UDP."""
    x, y, z = new_coords
    message = f"{x:.4f} {y:.4f} {z:.4f}"
    try:
        socket.sendto(message.encode(), (ip, port))
    except Exception as e:
        print(f"udp send error: {e}")