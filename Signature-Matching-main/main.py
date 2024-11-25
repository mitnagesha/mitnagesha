import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import os
import cv2
import logging
from signature import match
from PIL import Image, ImageTk

# Match Threshold
THRESHOLD = 80

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def browsefunc(ent):
    filename = askopenfilename(filetypes=[("image", ".jpeg"),
                                          ("image", ".png"),
                                          ("image", ".jpg"),])
    ent.delete(0, tk.END)
    ent.insert(tk.END, filename)

def capture_image_from_cam_into_temp(filename):
    try:
        logging.debug("Initializing camera...")
        cam = cv2.VideoCapture(0)
        
        if not cam.isOpened():
            raise RuntimeError("Could not access the camera.")
        
        logging.debug("Capturing image...")
        ret, frame = cam.read()
        if not ret:
            raise RuntimeError("Failed to capture image from camera.")
        
        cv2.imwrite(filename, frame)
        logging.debug("Image saved successfully.")
        cam.release()
    
    except Exception as e:
        logging.error(f"Error: {e}")
        messagebox.showerror("Error", str(e))

def captureImage(ent, sign):
    if sign == 1:
        filename = os.path.join(os.getcwd(), 'temp', 'test_img1.png')
    else:
        filename = os.path.join(os.getcwd(), 'temp', 'test_img2.png')
    
    capture_image_from_cam_into_temp(filename)
    ent.delete(0, tk.END)
    ent.insert(tk.END, filename)

def checkSimilarity(path1, path2):
    if not os.path.exists(path1) or not os.path.exists(path2):
        messagebox.showerror("Error", "One or both image paths are invalid.")
        return

    result = match(path1=path1, path2=path2)
    if result <= THRESHOLD:
        messagebox.showerror("Failure: Signatures Do Not Match", f"Signatures are {result} % similar!!")
    else:
        messagebox.showinfo("Success: Signatures Match", f"Signatures are {result} % similar!!")

def update_frame():
    global cam, frame
    ret, frame = cam.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)
    camera_label.after(10, update_frame)

def start_camera(window):
    global cam
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        logging.error("Could not access the camera.")
        messagebox.showerror("Error", "Could not access the camera.")
        return
    
    global camera_label
    camera_label = tk.Label(window)
    camera_label.pack()
    update_frame()

def capture_from_camera(ent, sign):
    global cam, frame
    if not cam:
        logging.error("No camera feed available.")
        messagebox.showerror("Error", "No camera feed available.")
        return

    if sign == 1:
        filename = os.path.join(os.getcwd(), 'temp', 'test_img1.png')
    else:
        filename = os.path.join(os.getcwd(), 'temp', 'test_img2.png')
    
    if cam:
        cv2.imwrite(filename, frame)
        logging.debug("Image captured and saved successfully.")
        ent.delete(0, tk.END)
        ent.insert(tk.END, filename)
    else:
        logging.error("No camera feed available.")
        messagebox.showerror("Error", "No camera feed available.")

def open_camera_window(ent, sign):
    camera_window = tk.Toplevel()
    camera_window.title("Camera Preview")
    camera_window.geometry("640x480")
    
    camera_frame = tk.Frame(camera_window, bg='blue', bd=5)
    camera_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    
    start_camera(camera_frame)
    
    capture_button = tk.Button(camera_window, text="Capture", command=lambda: capture_from_camera(ent, sign))
    capture_button.pack(pady=10)
    
    camera_window.protocol("WM_DELETE_WINDOW", lambda: close_camera_window(camera_window))

def close_camera_window(window):
    global cam
    if cam:
        cam.release()
    cv2.destroyAllWindows()
    window.destroy()

# Tkinter setup
root = tk.Tk()
root.title("Signature Matching")
root.geometry("600x800")

main_frame = tk.Frame(root, bg='red', bd=5)
main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

uname_label = tk.Label(main_frame, text="Compare Two Signatures:", font=10, bg='orange', fg='white')
uname_label.pack(pady=20)

# Signature 1 Widgets
img1_frame = tk.Frame(main_frame, bg='green')
img1_frame.pack(pady=10, fill=tk.X)

img1_message = tk.Label(img1_frame, text="Signature 1", font=10, bg='orange', fg='white')
img1_message.pack(side=tk.LEFT, padx=10)

image1_path_entry = tk.Entry(img1_frame, font=10)
image1_path_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

img1_capture_button = tk.Button(img1_frame, text="Capture", font=10, command=lambda: open_camera_window(ent=image1_path_entry, sign=1))
img1_capture_button.pack(side=tk.LEFT, padx=10)

img1_browse_button = tk.Button(img1_frame, text="Browse", font=10, command=lambda: browsefunc(ent=image1_path_entry))
img1_browse_button.pack(side=tk.LEFT, padx=10)

# Signature 2 Widgets
img2_frame = tk.Frame(main_frame, bg='yellow')
img2_frame.pack(pady=10, fill=tk.X)

img2_message = tk.Label(img2_frame, text="Signature 2", font=10, bg='black', fg='white')
img2_message.pack(side=tk.LEFT, padx=10)

image2_path_entry = tk.Entry(img2_frame, font=10)
image2_path_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

img2_capture_button = tk.Button(img2_frame, text="Capture", font=10, command=lambda: open_camera_window(ent=image2_path_entry, sign=2))
img2_capture_button.pack(side=tk.LEFT, padx=10)

img2_browse_button = tk.Button(img2_frame, text="Browse", font=10, command=lambda: browsefunc(ent=image2_path_entry))
img2_browse_button.pack(side=tk.LEFT, padx=10)

# Compare Button
compare_button = tk.Button(main_frame, text="Compare", font=10, command=lambda: checkSimilarity(
    path1=image1_path_entry.get(),
    path2=image2_path_entry.get()))
compare_button.pack(pady=20)

logging.debug("Starting Tkinter mainloop...")
root.mainloop()

# Release the camera when exiting
if cam:
    cam.release()
cv2.destroyAllWindows()
