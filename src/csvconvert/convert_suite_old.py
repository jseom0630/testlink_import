import os
import csv
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils

# 실행 파일의 디렉토리 경로
base_dir = os.path.dirname(os.path.abspath(__file__))

# CSV 파일 디렉토리 경로
csv_dir = os.path.join(base_dir, 'Testsuite', 'CSV')

# XML 파일 디렉토리 경로
xml_dir = os.path.join(base_dir, 'Testsuite', 'XML')
# CSV 파일 목록 가져오기
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# CSV 파일 목록 출력
print("CSV 파일 목록:")
for i, csv_file in enumerate(csv_files):
    print(f"{i+1}. {csv_file}")

# 사용자로부터 CSV 파일 선택
csv_index = int(input("변환할 CSV 파일 번호를 입력하세요: ")) - 1
csv_file = csv_files[csv_index]

# XML 파일 이름 생성
xml_name = os.path.splitext(csv_file)[0] + ".xml"
xml_path = os.path.join(xml_dir, xml_name)

# 중복된 파일명 처리
if os.path.exists(xml_path):
    i = 1
    while True:
        xml_name = os.path.splitext(csv_file)[0] + f"_{i}.xml"
        xml_path = os.path.join(xml_dir, xml_name)
        if not os.path.exists(xml_path):
            break
        i += 1

with open(os.path.join(csv_dir, csv_file), 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)
    suite_name = ''
    root = ET.Element('testsuite')
    for row in csvreader:
        if suite_name != row[0]:
            # Create new suite element
            suite_name = row[0]
            suite = ET.SubElement(root, 'testsuite')
            suite.set('name', suite_name)
            testcase = None
        if not testcase or testcase.get('name') != row[1]:
            # Create new testcase element
            testcase = ET.SubElement(suite, 'testcase')
            testcase.set('name', row[1])
            summary = ET.SubElement(testcase, 'summary')
            summary.text = row[2]
            preconditions = ET.SubElement(testcase, 'preconditions')
            preconditions.text = row[3]
            steps = ET.SubElement(testcase, 'steps')
        # Create step element
        if row[4]:
            step = ET.SubElement(steps, 'step')
            step_number = ET.SubElement(step, 'step_number')
            step_number.text = row[4]
            actions = ET.SubElement(step, 'actions')
            actions.text = row[5]
            expectedresults = ET.SubElement(step, 'expectedresults')
            expectedresults.text = row[6]
            
            
# XML 파일 저장
tree = ET.ElementTree(root)
tree.write(xml_path, encoding='utf-8', xml_declaration=True)

# 변환된 XML 파일 경로 출력
print(f"XML 파일이 {xml_path}로 변환되었습니다.")
