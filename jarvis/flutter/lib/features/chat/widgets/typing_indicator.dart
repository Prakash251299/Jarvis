import 'package:flutter/material.dart';
import '../../../core/constants/colors.dart';

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({super.key});

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(3, (index) {
            final t = (_controller.value + (index * 0.2)) % 1.0;
            final offset = (t < 0.5) ? (t * 2 * 6.0) : ((1.0 - t) * 2 * 6.0);
            return Container(
              margin: const EdgeInsets.symmetric(horizontal: 2),
              transform: Matrix4.translationValues(0, -offset, 0),
              width: 6,
              height: 6,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.primary,
              ),
            );
          }),
        );
      },
    );
  }
}
