from init_script import SessionLocal, PillInfo, FALLBACK_LABEL_PATH, DEFAULT_IMAGE_URL, log_info, log_warn, log_error
import os
import json

# DB 세션 시작
db = SessionLocal()

# 로그용 리스트
inserted_ids = []
skipped_ids = []
failed_ids = []

def insert_from_fallback_json():
    log_info("🚀 Fallback JSON 삽입 시작")

    for i in range(1, 11):
        base_folder = os.path.join(FALLBACK_LABEL_PATH, f"VL_{i}_단일")
        if not os.path.isdir(base_folder):
            log_warn(f"📁 폴더 없음: {base_folder}")
            continue

        for subfolder in os.listdir(base_folder):
            if not subfolder.endswith("_json"):
                continue

            class_id = subfolder.replace("_json", "")
            folder_path = os.path.join(base_folder, subfolder)

            if db.query(PillInfo).filter(PillInfo.class_id == class_id).first():
                skipped_ids.append(class_id)
                continue

            json_files = sorted(f for f in os.listdir(folder_path) if f.endswith(".json"))
            if not json_files:
                failed_ids.append(class_id)
                continue

            file_path = os.path.join(folder_path, json_files[0])  # 첫 번째 JSON만
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "images" not in data or not data["images"]:
                        failed_ids.append(class_id)
                        continue

                    image = data["images"][0]
                    image_url = image.get("img_key")
                    if not image_url or not image_url.startswith("http"):
                        image_url = DEFAULT_IMAGE_URL

                    pill = PillInfo(
                                class_id=class_id,
                                item_seq=image.get("item_seq"),
                                dl_name=image.get("dl_name"),              # ✅ 수정됨
                                dl_material=image.get("dl_material"),
                                dl_company=image.get("dl_company"),
                                di_company_mf=image.get("di_company_mf"),
                                di_class_no=image.get("di_class_no"),
                                di_etc_otc_code=image.get("di_etc_otc_code"),
                                di_edi_code=image.get("di_edi_code"),
                                img_key=image_url
                                
                                
)

                    db.add(pill)
                    inserted_ids.append(class_id)
                    log_info(f"✅ INSERT: {class_id} - {pill.item_name}")

            except Exception as e:
                log_error(f"❌ ERROR: {class_id} - {e}")
                failed_ids.append(class_id)
                continue

    db.commit()
    db.close()
    log_info(f"\n📦 삽입 완료: {len(inserted_ids)}개, SKIP: {len(skipped_ids)}개, 실패: {len(failed_ids)}개")

    # 결과 로그 파일 저장
    with open("inserted_class_ids.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(inserted_ids))
    with open("skipped_class_ids.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(skipped_ids))
    with open("failed_class_ids.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_ids))

    log_info("📝 삽입 로그 저장 완료 (inserted, skipped, failed)")

if __name__ == "__main__":
    insert_from_fallback_json()
