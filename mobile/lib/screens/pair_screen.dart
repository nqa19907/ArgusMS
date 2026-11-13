import 'package:flutter/material.dart';

import '../app_controller.dart';

class PairScreen extends StatefulWidget {
  const PairScreen({super.key, required this.controller});
  final AppController controller;
  @override
  State<PairScreen> createState() => _PairScreenState();
}

class _PairScreenState extends State<PairScreen> {
  final _link = TextEditingController();
  bool _showLink = false;

  @override
  void dispose() {
    _link.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final app = widget.controller;
    return Scaffold(
      appBar: AppBar(title: const Text('ArgusMS · Ghép thiết bị')),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 620),
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                const Icon(Icons.shield_outlined, size: 56),
                const SizedBox(height: 20),
                Text(
                  'Kết nối hệ thống giám sát',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 12),
                const Text(
                  'Nhờ SV2 tạo link ghép dùng một lần (120 giây), rồi dán vào bên dưới. '
                  'Không cần tài khoản người dùng. Chỉ ghép backend bạn tin cậy.',
                ),
                const SizedBox(height: 24),
                TextField(
                  controller: _link,
                  obscureText: !_showLink,
                  autocorrect: false,
                  enableSuggestions: false,
                  decoration: InputDecoration(
                    labelText: 'Link ghép thiết bị',
                    hintText: 'fallguard://pair?server=…&code=…&installation=…',
                    border: const OutlineInputBorder(),
                    suffixIcon: IconButton(
                      onPressed: () => setState(() => _showLink = !_showLink),
                      tooltip: _showLink ? 'Ẩn link' : 'Hiện link',
                      icon: Icon(
                        _showLink ? Icons.visibility_off : Icons.visibility,
                      ),
                    ),
                  ),
                  onSubmitted: app.busy ? null : (_) => app.pair(_link.text),
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: app.busy ? null : () => app.pair(_link.text),
                  icon: const Icon(Icons.link),
                  label: const Text('Ghép thiết bị'),
                ),
                OutlinedButton(
                  onPressed: app.busy
                      ? null
                      : () => app.checkHealth(_link.text),
                  child: const Text('Kiểm tra backend (không dùng mã ghép)'),
                ),
                if (app.busy)
                  const Padding(
                    padding: EdgeInsets.all(12),
                    child: LinearProgressIndicator(),
                  ),
                if (app.error != null)
                  _message(
                    app.error!,
                    Theme.of(context).colorScheme.errorContainer,
                  ),
                if (app.notice != null)
                  _message(
                    app.notice!,
                    Theme.of(context).colorScheme.secondaryContainer,
                  ),
                const SizedBox(height: 20),
                const Text(
                  'Máy ảo và backend cùng Mac: dùng 10.0.2.2. '
                  'Backend trên máy SV2: dùng IP LAN của máy SV2. Địa chỉ phải được đặt trong link ghép.',
                ),
                const SizedBox(height: 16),
                TextButton(
                  onPressed: app.busy ? null : app.useDemo,
                  child: const Text('Xem demo dữ liệu mẫu'),
                ),
                TextButton(
                  onPressed: app.busy
                      ? null
                      : () => app.unpair(localOnly: true),
                  child: const Text('Xóa thông tin ghép cũ trên app'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _message(String text, Color color) => Container(
    margin: const EdgeInsets.only(top: 12),
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(
      color: color,
      borderRadius: BorderRadius.circular(12),
    ),
    child: Text(text),
  );
}
