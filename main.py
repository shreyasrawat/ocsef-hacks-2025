from picamera2 import Picamera2
import cv2
import gpiozero
import time

# Function to calculate distance
def distance_to_camera(knownWidth, focalLength, perWidth):
    distance = (knownWidth * focalLength) / perWidth
    return distance

# Function to find focal length
def find_focal_length(known_distance, known_width, image_width_in_pixels):
    focal_length = (image_width_in_pixels * known_distance) / known_width
    return focal_length

# Define known properties
KNOWN_WIDTH = 274.32  # Actual width of the object (cm)
KNOWN_DISTANCE = 30.0  # Known distance to the object during calibration (cm)
KNOWN_IMAGE_WIDTH = 300  # Width of the object in pixels at known distance

FOCAL_LENGTH = find_focal_length(KNOWN_DISTANCE, KNOWN_WIDTH, KNOWN_IMAGE_WIDTH)

# Load the cascade for object detection
cascade_src = 'cars.xml'  # Make sure this path is correct
car_cascade = cv2.CascadeClassifier(cascade_src)
led = gpiozero.LED(2)
time.sleep(1)
# Initialize PiCamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

while True:
    img = picam2.capture_array()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cars = car_cascade.detectMultiScale(gray, 1.1, 1)

    for (x, y, w, h) in cars:
        # Draw rectangle around detected car
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Calculate distance
        distance = distance_to_camera(KNOWN_WIDTH, FOCAL_LENGTH, w)
        
        if distance < 49:
            led.on()
        else:
            led.off()
        # Put distance text above the rectangle
        cv2.putText(img, f"Distance: {distance:.2f} cm", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show the video frame
    #cv2.imshow('video', img)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
