"""Adaptateurs vision (port `VideoSource`, `HornetDetector`).

Les dépendances lourdes (`cv2`, `torch`, YOLOv5) sont importées en lazy à
l'intérieur des classes : importer ce package ne requiert pas l'extra
`vision`. Installer avec `pip install aristech[vision]` pour les utiliser.
"""
