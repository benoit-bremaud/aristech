"""Vision adapters (`VideoSource`, `HornetDetector` ports).

Heavy dependencies (`cv2`, `torch`, YOLOv5) are imported lazily inside the classes:
importing this package does not need the `vision` extra. Install it with
`pip install aristech[vision]` to use them.
"""
