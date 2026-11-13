import 'package:flutter/material.dart';

import '../app_controller.dart';

const _cameraLabels = {
  'STOPPED': 'Chưa bật camera',
  'CONNECTING': 'Đang kết nối',
  'CONNECTED': 'Có hình',
  'RECONNECTING': 'Đang kết nối lại',
  'ERROR': 'Lỗi camera',
};
const _aiLabels = {
  'LOADING': 'Đang tải',
  'WARMUP': 'Đang khởi động',
  'READY': 'Sẵn sàng',
  'DEGRADED': 'Chất lượng giảm',
  'ERROR': 'Nhận diện không hoạt động',
};

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key, required this.controller});
  final AppController controller;

  @override
  Widget build(BuildContext context) {
    final app = controller;
    final status = app.status;
    final session = app.pairing;
    final event = app.lastEvent;
    return Scaffold(
      appBar: AppBar(
        title: Text(app.isDemo ? 'ArgusMS · DEMO' : 'ArgusMS · Theo dõi'),
        actions: [
          IconButton(
            tooltip: 'Làm mới status',
            onPressed: app.isDemo ? app.cycleDemo : () => app.refresh(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                if (app.isDemo)
                  _banner(
                    context,
                    'DỮ LIỆU MẪU · không kết nối backend, không phải kết quả AI.',
                  ),
                if (app.error != null)
                  _banner(context, app.error!, error: true),
                if (app.notice != null) _banner(context, app.notice!),
                _card(context, 'Kết nối', [
                  if (session != null) Text('Backend: ${session.server}'),
                  Text(
                    app.isDemo
                        ? 'Backend: demo offline'
                        : app.backendOnline
                        ? 'HTTP: đã nhận status'
                        : 'HTTP: chưa có status mới / mất kết nối',
                  ),
                  Text('WebSocket: ${app.wsState}'),
                  if (app.statusReceivedAt != null)
                    Text('Lần nhận status: ${app.statusReceivedAt!.toLocal()}'),
                  if (!app.backendOnline && status != null && !app.isDemo)
                    const Text(
                      'Dữ liệu bên dưới là lần nhận trước; chưa xác nhận trạng thái hiện tại.',
                    ),
                  if (session != null)
                    SelectableText('Device ID: ${session.deviceId}'),
                  if (session != null)
                    SelectableText('Installation: ${session.installationId}'),
                ]),
                if (status == null)
                  const Padding(
                    padding: EdgeInsets.all(20),
                    child: Text(
                      'Đang chờ status. App sẽ tự thử lại khi đang mở.',
                    ),
                  ),
                if (status != null) ...[
                  _card(context, 'Camera · ${status.cameraId}', [
                    Text(
                      '${_cameraLabels[status.cameraState]} (${status.cameraState})',
                    ),
                    if (status.lastFrameAgeMs != null)
                      Text('Tuổi frame gần nhất: ${status.lastFrameAgeMs} ms'),
                    const Text('Nhập RTSP và xem hình được bổ sung ở tuần 2.'),
                  ]),
                  _card(context, 'AI', [
                    Text('${_aiLabels[status.aiState]} (${status.aiState})'),
                    Text('Mode: ${status.aiMode} · Model: ${status.modelId}'),
                    if (status.aiMode == 'mock' ||
                        status.modelId.startsWith('mock'))
                      const Text(
                        'MOCK: kết quả giả để ghép hệ thống, không phải AI thật.',
                      ),
                    Text('FPS xử lý: ${status.processedFps}'),
                    if (status.cameraState == 'CONNECTED' &&
                        status.aiState == 'ERROR')
                      const Text(
                        'Camera có hình nhưng nhận diện không hoạt động.',
                      ),
                  ]),
                ],
                if (!app.isDemo)
                  _card(context, 'Thông báo', [
                    Text(app.notifications.state),
                    if (app.pushError != null) Text(app.pushError!),
                    Text('FCM đã nhận khi app mở: ${app.foregroundPushCount}'),
                    Text('Lần mở từ notification: ${app.openedPushCount}'),
                    Text(
                      app.pushSynced
                          ? 'Endpoint: backend đã xác nhận lưu'
                          : 'Endpoint: chưa đồng bộ backend',
                    ),
                    if (status != null)
                      Text('Lần gửi của backend: ${status.lastSendState}'),
                    const SizedBox(height: 8),
                    FilledButton.tonal(
                      onPressed:
                          app.registeringPush ||
                              app.busy ||
                              !app.notifications.ready
                          ? null
                          : () => app.registerPush(),
                      child: Text(
                        app.registeringPush
                            ? 'Đang đăng ký…'
                            : 'Bật / đăng ký lại thông báo',
                      ),
                    ),
                    OutlinedButton(
                      onPressed: app.busy || !app.pushSynced
                          ? null
                          : () => app.sendTest(),
                      child: const Text('Yêu cầu backend gửi thử'),
                    ),
                    const Text(
                      'Để xác nhận push nền: nhấn Home trên Android, rồi nhờ SV2 gửi từ script. '
                      'Sự kiện qua WS chưa chứng minh FCM hoạt động.',
                    ),
                  ]),
                if (app.busy || app.registeringPush)
                  const LinearProgressIndicator(),
                if (event != null)
                  _card(
                    context,
                    event.isTest ? 'THÔNG BÁO THỬ' : 'Sự kiện nghi ngã',
                    [
                      Text(event.message),
                      Text('Nguồn nhận: ${app.eventSource}'),
                      Text('Camera: ${event.cameraId}'),
                      Text('Thời gian: ${event.confirmedAt.toLocal()}'),
                      SelectableText('Event ID: ${event.eventId}'),
                      TextButton(
                        onPressed: app.dismissEvent,
                        child: const Text('Đóng thẻ trên app'),
                      ),
                      const Text(
                        'Tuần 1 chỉ hiển thị sự kiện; chưa phát alarm vòng lặp hoặc gửi ack.',
                      ),
                    ],
                  ),
                if (app.isDemo) ...[
                  OutlinedButton(
                    onPressed: app.cycleDemo,
                    child: const Text('Đổi trạng thái mẫu'),
                  ),
                  FilledButton(
                    onPressed: app.demoEvent,
                    child: const Text('Tạo sự kiện mẫu'),
                  ),
                  TextButton(
                    onPressed: () => app.unpair(localOnly: true),
                    child: const Text('Thoát demo'),
                  ),
                ] else ...[
                  const SizedBox(height: 12),
                  OutlinedButton(
                    onPressed: app.busy ? null : () => _unpair(context),
                    child: const Text('Hủy ghép thiết bị'),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _unpair(BuildContext context) async {
    final choice = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hủy ghép thiết bị?'),
        content: const Text(
          'Thu hồi trên backend sẽ ngừng gửi đến thiết bị này. '
          'Nếu chọn chỉ quên trên app khi offline, cần nhờ SV2 thu hồi phía server sau.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Giữ lại'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, 'local'),
            child: const Text('Chỉ quên trên app'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, 'server'),
            child: const Text('Thu hồi trên backend'),
          ),
        ],
      ),
    );
    if (choice != null) await controller.unpair(localOnly: choice == 'local');
  }

  Widget _card(BuildContext context, String title, List<Widget> children) =>
      Card(
        margin: const EdgeInsets.only(bottom: 16),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 10),
              ...children.map(
                (child) => Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: child,
                ),
              ),
            ],
          ),
        ),
      );

  Widget _banner(BuildContext context, String text, {bool error = false}) =>
      Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: error
              ? Theme.of(context).colorScheme.errorContainer
              : Theme.of(context).colorScheme.secondaryContainer,
        ),
        child: Text(text),
      );
}
