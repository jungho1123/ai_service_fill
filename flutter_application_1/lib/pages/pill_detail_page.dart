// lib/pages/pill_detail_page.dart
import 'package:flutter/material.dart';

class PillDetailPage extends StatelessWidget {
  final Map<String, dynamic> pill;
  const PillDetailPage({super.key, required this.pill});

  final String defaultImageUrl = "http://10.0.2.2:8000/static/default-pill.png";

  @override
  Widget build(BuildContext context) {
    if (pill.isEmpty) {
      return const Scaffold(
        body: Center(child: Text(" 약 정보가 존재하지 않습니다.")),
      );
    }

    final pillLower = pill.map((key, value) => MapEntry(key.toLowerCase(), value));

    final imageUrl = pillLower['itemimage'] ??
        pillLower['item_image'] ??
        pillLower['img_key'] ??
        defaultImageUrl;

    final isApi = pillLower['source'] == 'api';

    return Scaffold(
      appBar: AppBar(title: const Text(" 약 상세 정보")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Image.network(
              imageUrl,
              height: 160,
              width: double.infinity,
              fit: BoxFit.contain,
              errorBuilder: (_, __, ___) => Image.network(
                defaultImageUrl,
                height: 160,
              ),
            ),
            const SizedBox(height: 16),
            ...(isApi ? _buildApiDetails(pillLower) : _buildDbDetails(pillLower)),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
              decoration: BoxDecoration(
                color: isApi ? Colors.green[100] : Colors.orange[100],
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text("출처: ${isApi ? '공공데이터 API' : '내부 데이터베이스'}"),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildApiDetails(Map<String, dynamic> pill) => [
        _buildDetailItem(" 약 이름", pill['itemname']),
        _buildDetailItem(" 제약사", pill['entpname']),
        _buildDetailItem(" 효능", pill['efcyqesitm']),
        _buildDetailItem(" 복용 방법", pill['usemethodqesitm']),
        _buildDetailItem(" 주의사항", pill['atpnqesitm']),
        _buildDetailItem(" 경고", pill['atpnwarnqesitm']),
        _buildDetailItem(" 상호작용", pill['intrcqesitm']),
        _buildDetailItem(" 부작용", pill['seqesitm']),
        _buildDetailItem(" 보관법", pill['depositmethodqesitm']),
        _buildDetailItem(" itemSeq", pill['itemseq']),
        _buildDetailItem(" 사업자등록번호", pill['bizrno']),
      ];

  List<Widget> _buildDbDetails(Map<String, dynamic> pill) => [
        _buildDetailItem(" 약 이름", pill['dl_name']),
        _buildDetailItem(" 제약사", pill['dl_company']),
        _buildDetailItem(" 성분", pill['dl_material']),
        _buildDetailItem(" 제조사", pill['di_company_mf']),
        _buildDetailItem(" 분류", pill['di_class_no']),
        _buildDetailItem(" 전문/일반", pill['di_etc_otc_code']),
        _buildDetailItem(" EDI 코드", pill['di_edi_code']),
        _buildDetailItem(" item_seq", pill['item_seq']),
      ];

  Widget _buildDetailItem(String title, dynamic value) {
    if (value == null || value.toString().trim().isEmpty || value.toString().toLowerCase() == 'null') {
      return const SizedBox.shrink();
    }
    return Padding(
      padding: const EdgeInsets.only(bottom: 10.0),
      child: SelectableText(
        "$title: $value",
        style: const TextStyle(fontSize: 16, height: 1.5),
      ),
    );
  }
}
