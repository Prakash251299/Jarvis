import 'package:flutter/material.dart';
import '../../../core/constants/colors.dart';

class WaveformAnimation extends StatelessWidget {
  final double level;

  const WaveformAnimation({super.key, required this.level});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (index) {
        final scale = (0.3 + (level * (0.5 + 0.5 * (index % 3)))).clamp(0.2, 1.0);
        return AnimatedContainer(
          duration: const Duration(milliseconds: 100),
          margin: const EdgeInsets.symmetric(horizontal: 2),
          width: 4,
          height: 24 * scale,
          decoration: BoxDecoration(
            color: AppColors.recordingRed,
            borderRadius: BorderRadius.circular(2),
          ),
        );
      }),
    );
  }
}
