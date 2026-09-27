import 'package:flutter/material.dart';
import '../core/constants/colors.dart';

class JarvisAvatar extends StatelessWidget {
  final double size;
  final bool isPulsing;

  const JarvisAvatar({super.key, this.size = 36.0, this.isPulsing = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: const LinearGradient(
          colors: [AppColors.primaryLight, AppColors.primary, AppColors.primaryDark],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: isPulsing
            ? [
                BoxShadow(
                  color: AppColors.primary.withValues(alpha: 0.5),
                  blurRadius: 10,
                  spreadRadius: 2,
                )
              ]
            : null,
      ),
      child: Center(
        child: Text(
          'J',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: size * 0.5,
          ),
        ),
      ),
    );
  }
}

class UserAvatar extends StatelessWidget {
  final double size;

  const UserAvatar({super.key, this.size = 36.0});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.userBubbleLight,
      ),
      child: Icon(
        Icons.person,
        color: Colors.white,
        size: size * 0.6,
      ),
    );
  }
}
