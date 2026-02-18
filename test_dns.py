import socket

host = "db.zgkagjttiinouppofdhs.supabase.co"
try:
    addr = socket.gethostbyname(host)
    print(f"IP: {addr}")
except Exception as e:
    print(f"Error: {e}")
