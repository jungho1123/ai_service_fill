// test/widget_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_application_1/main.dart';

void main() {
  testWidgets('앱이 정상적으로 렌더링되는지 테스트', (WidgetTester tester) async {
    // PillApp 위젯을 렌더링
    await tester.pumpWidget(const PillApp());

    // 메인 타이틀 텍스트가 존재하는지 확인
    expect(find.text('약 정보 서비스'), findsOneWidget);

    // 버튼들이 존재하는지 확인
    expect(find.text('🔍 약 이름으로 검색'), findsOneWidget);
    expect(find.text('📷 이미지로 예측'), findsOneWidget);
  });
}