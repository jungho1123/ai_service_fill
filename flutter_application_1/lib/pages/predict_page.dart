// lib/pages/predict_page.dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:image_picker/image_picker.dart';

class PredictPageWidget extends StatefulWidget {
  const PredictPageWidget({super.key});

  @override
  State<PredictPageWidget> createState() => _PredictPageWidgetState();
}

class _PredictPageWidgetState extends State<PredictPageWidget> {
  File? _image;
  Map<String, dynamic>? _pillData;
  bool _loading = false;
  String? _error;

  final String defaultImageUrl = "http://10.0.2.2:8000/static/default-pill.png";

  Future<void> pickAndPredict() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile == null) return;

    setState(() {
      _image = File(pickedFile.path);
      _loading = true;
      _pillData = null;
      _error = null;
    });

    final uri = Uri.parse("http://10.0.2.2:8000/predict");
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('file', _image!.path));

    try {
      final response = await request.send();
      final bytes = await response.stream.toBytes();
      final respStr = utf8.decode(bytes);
      final data = json.decode(respStr);

      setState(() {
        if (data["source"] == "api" || data["source"] == "fallback") {
          _pillData = data;
        } else {
          _error = data['message'] ?? '결과를 받아오지 못했습니다';
        }
      });
    } catch (e) {
      setState(() {
        _error = ' 예측 실패: $e';
      });
    } finally {
      setState(() => _loading = false);
    }
  }

  Widget _buildApiInfo(Map<String, dynamic> data) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _info(" 약 이름", data["itemName"]),
        _info(" 제약사", data["entpName"]),
        _info(" 효능", data["efcyQesitm"]),
        _info(" 복용 방법", data["useMethodQesitm"]),
        _info(" 주의사항", data["atpnQesitm"]),
        _info(" 경고", data["atpnWarnQesitm"]),
        _info(" 상호작용", data["intrcQesitm"]),
        _info(" 부작용", data["seQesitm"]),
        _info(" 보관법", data["depositMethodQesitm"]),
        _info(" itemSeq", data["itemSeq"]),
        _info(" 사업자등록번호", data["bizrno"]),
      ],
    );
  }

  Widget _buildDbInfo(Map<String, dynamic> data) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _info(" 약 이름", data["dl_name"]),
        _info(" 제약사", data["dl_company"]),
        _info(" 성분", data["dl_material"]),
        _info(" 제조사", data["di_company_mf"]),
        _info(" 분류", data["di_class_no"]),
        _info(" 전문/일반", data["di_etc_otc_code"]),
        _info(" EDI 코드", data["di_edi_code"]),
        _info(" item_seq", data["item_seq"]),
      ],
    );
  }

  Widget _info(String title, dynamic value) {
    if (value == null || value.toString().trim().isEmpty || value.toString().toLowerCase() == 'null') {
      return const SizedBox.shrink();
    }
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: SelectableText("$title: $value", style: const TextStyle(fontSize: 16, height: 1.4)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text(" 약 이미지 예측")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(  
          children: [
            if (_image != null)
              Image.file(_image!, height: 200)
            else
              const Text("이미지를 선택해주세요."),

            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: pickAndPredict,
              child: const Text("이미지 선택 & 예측"),
            ),
            const SizedBox(height: 16),

            if (_loading) const CircularProgressIndicator(),
            if (_error != null) ...[
              const SizedBox(height: 16),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
            if (_pillData != null) ...[
              const SizedBox(height: 20),
              Image.network(
                _pillData!["img_key"] ?? _pillData!["itemImage"] ?? defaultImageUrl,
                height: 120,
              ),
              const SizedBox(height: 16),

              if (_pillData!["confidence"] != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Text(
                    "예측 신뢰도: ${(_pillData!["confidence"] * 100).toStringAsFixed(2)}%",
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),

              _pillData!["source"] == "api"
                  ? _buildApiInfo(_pillData!)
                  : _buildDbInfo(_pillData!),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 10),
                decoration: BoxDecoration(
                  color: _pillData!["source"] == "api" ? Colors.green[100] : Colors.orange[100],
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text("출처: ${_pillData!["source"] == "api" ? "공공데이터 API" : "내부 DB"}"),
              ),
            ]
          ],
        ),
      ),
    );
  }
}
