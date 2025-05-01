from ultralytics import YOLO
model = YOLO("yolov8n.pt")
model.train(data='signature.yaml', epochs=10, imgsz=640)