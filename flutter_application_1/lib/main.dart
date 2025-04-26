// lib/main.dart
import 'package:flutter/material.dart';
import 'pages/search_page.dart' as search;
import 'pages/predict_page.dart' as predict;

void main() {
  runApp(const PillApp());
}

class PillApp extends StatelessWidget {
  const PillApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '약 정보 서비스',
      theme: ThemeData(primarySwatch: Colors.teal),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('약 정보 서비스')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const search.SearchPageWidget()),
                );
              },
              icon: const Icon(Icons.search),
              label: const Text(" 약 이름으로 검색"),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const predict.PredictPageWidget()),
                );
              },
              icon: const Icon(Icons.camera_alt),
              label: const Text(" 이미지로 예측"),
            ),
          ],
        ),
      ),
    );
  }
}
