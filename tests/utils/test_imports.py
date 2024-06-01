# tests/test_imports.py

def test_imports():
    try:
        import src.coil_gun_control
        import src.distance_measurement
        import src.hornet_detection
        import src.image_processing
        import src.main
        import src.sound_detection
        import src.utils
        import src.video_capture
        import src.training.train_distance_model
        import src.training.train_image_model
        import src.training.train_sound_model
        import src.modules.connect
        import src.modules.solar
        import src.modules.sonar
        import src.modules.target
    except ImportError as e:
        assert False, f"Module import failed: {e}"
