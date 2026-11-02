# Live RF-DETR throughput on the laptop CPU

RF-DETR Small at the ACT threshold 0.45 runs at 16–44 FPS on a 13th-gen Intel i9 laptop CPU
(detect latency p50 18–37 ms), after a 9–17 s warm-up that loads the model; this is the baseline
the bench Pi 5 will be compared with (issue #140).

## Set-up

- Machine: Intel Core i9-13900H (20 threads, torch uses 14), no GPU used; Python 3.11, torch 2.15,
  rfdetr 1.11.2, OpenCV 5.0.
- Model: checkpoint sha256 `3df5a250d9cf3dc837a86376b62b634d0f693d202288a782bd46cb8cf992fcab`
  (no "unmeasured checkpoint" warning).
- Video: 60 test-v1 images resized to 640×480 and written as a 10 FPS mp4 (no real hive video is
  available locally yet). Frames are read as fast as the pipeline allows.

```bash
python -m aristech.interface.cli.main --video sample.mp4 \
    --detector rfdetr --checkpoint data/runs/prefield-small/checkpoint_best_total.pth
```

## Results (three runs)

| Run | Warm-up | FPS end to end | p50 latency | p95 latency |
|---:|---:|---:|---:|---:|
| 1 | 12.4 s | 40.2 | 22.6 ms | 28.3 ms |
| 2 | 9.4 s | 44.5 | 18.3 ms | 27.4 ms |
| 3 | 17.3 s | 16.4 | 36.6 ms | 122.5 ms |

Each run: 16 ACT, 48 ABSTAIN. Run 3 shared the CPU with other work: the spread shows the
figures depend on load, so the Pi 5 measurement should run on an idle board.

## Limits

- Still images stitched into a video, not hive footage: fine for throughput, not for accuracy.
- "End to end" counts video decode, detection and decision, not the warm-up frame.
