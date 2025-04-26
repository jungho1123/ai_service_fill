// lib/pages/search_page.dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'pill_detail_page.dart';
import 'dart:async';

class SearchPageWidget extends StatefulWidget {
  const SearchPageWidget({super.key});

  @override
  State<SearchPageWidget> createState() => _SearchPageWidgetState();
}

class _SearchPageWidgetState extends State<SearchPageWidget> {
  final TextEditingController _controller = TextEditingController();
  List<Map<String, dynamic>> _results = [];
  bool _isLoading = false;
  Timer? _debounce;

  final String defaultImageUrl = "http://10.0.2.2:8000/static/default-pill.png";

  Future<void> _search(String name) async {
    if (name.trim().isEmpty) return;
    setState(() {
      _isLoading = true;
      _results = [];
    });

    final url = Uri.parse("http://10.0.2.2:8000/search?name=${Uri.encodeComponent(name)}");
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        if (data is List) {
          setState(() {
            _results = List<Map<String, dynamic>>.from(data);
          });
        } else {
          setState(() => _results = []);
        }
      } else {
        setState(() => _results = []);
      }
    } catch (e) {
      setState(() => _results = []);
    }
    setState(() => _isLoading = false);
  }

  void _onChanged(String value) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      _search(value);
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("🔍 약 검색")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      labelText: "약 이름 입력",
                      border: OutlineInputBorder(),
                    ),
                    onChanged: _onChanged,
                    onSubmitted: _search,
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _search(_controller.text),
                  child: const Text("검색"),
                )
              ],
            ),
            const SizedBox(height: 20),
            if (_isLoading) const CircularProgressIndicator(),
            if (!_isLoading && _results.isEmpty && _controller.text.isNotEmpty)
              const Text("검색 결과가 없습니다."),
            if (_results.isNotEmpty)
              Expanded(
                child: ListView.builder(
                  itemCount: _results.length,
                  itemBuilder: (context, index) {
                    final pill = _results[index];
                    final imageUrl = pill['itemImage'] ?? defaultImageUrl;
                    return Card(
                      child: ListTile(
                        leading: Image.network(imageUrl, width: 50, height: 50, errorBuilder: (_, __, ___) => Image.network(defaultImageUrl, width: 50, height: 50)),
                        title: Text(pill['itemName'] ?? '-'),
                        subtitle: Text(pill['entpName'] ?? '-'),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => PillDetailPage(pill: pill),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
