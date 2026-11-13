import 'dart:async';

import 'package:flutter/material.dart';

import 'app_controller.dart';
import 'screens/home_screen.dart';
import 'screens/pair_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ArgusApp());
}

class ArgusApp extends StatefulWidget {
  const ArgusApp({super.key, this.controller, this.initialize = true});
  final AppController? controller;
  final bool initialize;

  @override
  State<ArgusApp> createState() => _ArgusAppState();
}

class _ArgusAppState extends State<ArgusApp> with WidgetsBindingObserver {
  late final AppController controller;

  @override
  void initState() {
    super.initState();
    controller = widget.controller ?? AppController();
    WidgetsBinding.instance.addObserver(this);
    if (widget.initialize) unawaited(controller.initialize());
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // Permission dialogs may cause inactive. Pause only on actual background.
    if (state == AppLifecycleState.resumed) controller.setForeground(true);
    if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.detached) {
      controller.setForeground(false);
    }
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'ArgusMS',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff176858)),
      useMaterial3: true,
    ),
    home: AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        if (controller.loading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        return controller.hasSession
            ? HomeScreen(controller: controller)
            : PairScreen(controller: controller);
      },
    ),
  );

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    if (widget.controller == null) controller.dispose();
    super.dispose();
  }
}
