import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app_controller.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('offline demo is labeled and camera/AI states stay separate', (
    tester,
  ) async {
    final controller = AppController()..loading = false;
    await tester.pumpWidget(
      ArgusApp(controller: controller, initialize: false),
    );
    expect(find.text('Ghép thiết bị'), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Xem demo dữ liệu mẫu'),
      200,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.text('Xem demo dữ liệu mẫu'));
    await tester.pumpAndSettle();
    expect(find.textContaining('DỮ LIỆU MẪU'), findsOneWidget);
    controller.cycleDemo();
    await tester.pump();
    await tester.scrollUntilVisible(
      find.text('Camera có hình nhưng nhận diện không hoạt động.'),
      200,
      scrollable: find.byType(Scrollable).first,
    );
    expect(
      find.text('Camera có hình nhưng nhận diện không hoạt động.'),
      findsOneWidget,
    );
    controller.demoEvent();
    await tester.pump();
    await tester.scrollUntilVisible(
      find.text('THÔNG BÁO THỬ'),
      200,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('THÔNG BÁO THỬ'), findsOneWidget);
    await tester.pumpWidget(const SizedBox.shrink());
    controller.dispose();
    await tester.pump();
  });
}
