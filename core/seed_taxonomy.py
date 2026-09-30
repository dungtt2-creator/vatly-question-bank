# -*- coding: utf-8 -*-
"""
Seed taxonomy 4 cấp từ CHƯƠNG TRÌNH GDPT 2018 MÔN VẬT LÍ
(Thông tư 32/2018/TT-BGDĐT ngày 26/12/2018 của Bộ trưởng Bộ GDĐT).

Mạch nội dung (cấp 1) là nhóm tổng hợp vận hành cho ngân hàng câu hỏi,
được xây dựng TỪ các nội dung chính thức trong CTGDPT 2018 (cấp 2 lấy đúng
tên nội dung của chương trình, kèm lớp). Yêu cầu cần đạt (cấp 4) trích
nguyên văn từ chương trình — không suy diễn, không bịa.
"""
SOURCE_DEFAULT = "Thông tư 32/2018/TT-BGDĐT – CTGDPT 2018 môn Vật lí"

# Các mạch nội dung (cấp 1)
STRANDS = [
    "Mở đầu",
    "Cơ học",
    "Sóng học",
    "Nhiệt học",
    "Điện học",
    "Từ học",
    "Quang học",
    "Vật lí hạt nhân và phóng xạ",
    "Vật lí hiện đại",
    "Trái Đất và bầu trời",
]

# Bảng nội dung: (mạch, grade, nội dung, [ (đơn vị kiến thức, [YCCĐ,...]), ... ])
CONTENTS = [
    # ---------------- MỞ ĐẦU (Lớp 10) ----------------
    ("Mở đầu", "Lớp 10", "Giới thiệu mục đích học tập môn Vật lí", [
        ("Đối tượng và mục tiêu của Vật lí học", [
            "Nêu được đối tượng nghiên cứu của Vật lí học và mục tiêu của môn Vật lí.",
            "Phân tích được một số ảnh hưởng của vật lí đối với cuộc sống, đối với sự phát triển của khoa học, công nghệ và kĩ thuật.",
            "Nêu được ví dụ chứng tỏ kiến thức, kĩ năng vật lí được sử dụng trong một số lĩnh vực khác nhau.",
        ]),
        ("Phương pháp nghiên cứu vật lí và tiến trình tìm hiểu tự nhiên", [
            "Nêu được một số ví dụ về phương pháp nghiên cứu vật lí (phương pháp thực nghiệm và phương pháp lí thuyết).",
            "Mô tả được các bước trong tiến trình tìm hiểu thế giới tự nhiên dưới góc độ vật lí.",
        ]),
        ("Sai số phép đo và an toàn trong học tập Vật lí", [
            "Thảo luận để nêu được một số loại sai số đơn giản hay gặp khi đo các đại lượng vật lí và cách khắc phục chúng.",
            "Thảo luận để nêu được các quy tắc an toàn trong nghiên cứu và học tập môn Vật lí.",
        ]),
    ]),
    ("Mở đầu", "Lớp 10", "Vật lí trong một số ngành nghề (Chuyên đề 10.1)", [
        ("Sơ lược về sự phát triển của vật lí học", [
            "Nêu được sơ lược sự ra đời và những thành tựu ban đầu của vật lí thực nghiệm.",
            "Nêu được sơ lược vai trò của cơ học Newton đối với sự phát triển của Vật lí học.",
            "Liệt kê được một số nhánh nghiên cứu chính của vật lí cổ điển.",
            "Nêu được sự khủng hoảng của vật lí cuối thế kỉ XIX, tiền đề cho sự ra đời của vật lí hiện đại.",
            "Liệt kê được một số lĩnh vực chính của vật lí hiện đại.",
        ]),
        ("Giới thiệu các lĩnh vực nghiên cứu trong vật lí học", [
            "Nêu được đối tượng nghiên cứu; liệt kê được một vài mô hình lí thuyết đơn giản, một số phương pháp thực nghiệm của một số lĩnh vực chính của vật lí hiện đại.",
        ]),
        ("Giới thiệu các ứng dụng của vật lí trong một số ngành nghề", [
            "Mô tả được ví dụ thực tế về việc sử dụng kiến thức vật lí trong một số lĩnh vực (Quân sự; Công nghiệp hạt nhân; Khí tượng; Nông nghiệp, Lâm nghiệp; Tài chính; Điện tử; Cơ khí, tự động hoá; Thông tin, truyền thông; Nghiên cứu khoa học).",
        ]),
    ]),
    ("Mở đầu", "Lớp 10", "Vật lí với giáo dục về bảo vệ môi trường (Chuyên đề 10.3)", [
        ("Sự cần thiết phải bảo vệ môi trường", [
            "Thảo luận để nêu được sự cần thiết bảo vệ môi trường trong chiến lược phát triển của các quốc gia.",
            "Thảo luận để nêu được vai trò của cá nhân và cộng đồng trong bảo vệ môi trường.",
        ]),
        ("Vật lí với giáo dục bảo vệ môi trường", [
            "Thảo luận để nêu được tác động của việc sử dụng năng lượng hiện nay đối với môi trường, kinh tế và khí hậu Việt Nam.",
            "Thảo luận để nêu được sơ lược về các chất ô nhiễm trong nhiên liệu hoá thạch, mưa axit, năng lượng hạt nhân, sự suy giảm tầng ozon, sự biến đổi khí hậu.",
            "Thảo luận để phân loại được năng lượng hoá thạch và năng lượng tái tạo; nêu được vai trò của năng lượng tái tạo.",
        ]),
    ]),

    # ---------------- CƠ HỌC ----------------
    ("Cơ học", "Lớp 10", "Động học", [
        ("Mô tả chuyển động", [
            "Lập luận để rút ra được công thức tính tốc độ trung bình, định nghĩa được tốc độ theo một phương.",
            "Từ hình ảnh hoặc ví dụ thực tiễn, định nghĩa được độ dịch chuyển; so sánh được quãng đường đi được và độ dịch chuyển.",
            "Dựa vào định nghĩa tốc độ theo một phương và độ dịch chuyển, rút ra được công thức tính và định nghĩa được vận tốc.",
            "Thực hiện thí nghiệm (hoặc dựa trên số liệu cho trước), vẽ được đồ thị độ dịch chuyển – thời gian trong chuyển động thẳng; tính được tốc độ từ độ dốc của đồ thị.",
            "Xác định được độ dịch chuyển tổng hợp, vận tốc tổng hợp; vận dụng được công thức tính tốc độ, vận tốc.",
            "Thảo luận để thiết kế phương án hoặc lựa chọn phương án và thực hiện phương án, đo được tốc độ bằng dụng cụ thực hành.",
            "Mô tả được một vài phương pháp đo tốc độ thông dụng và đánh giá được ưu, nhược điểm của chúng.",
        ]),
        ("Chuyển động biến đổi", [
            "Thực hiện thí nghiệm và lập luận dựa vào sự biến đổi vận tốc trong chuyển động thẳng, rút ra được công thức tính gia tốc; nêu được ý nghĩa, đơn vị của gia tốc.",
            "Thực hiện thí nghiệm (hoặc dựa trên số liệu cho trước), vẽ được đồ thị vận tốc – thời gian trong chuyển động thẳng.",
            "Vận dụng đồ thị vận tốc – thời gian để tính được độ dịch chuyển và gia tốc trong một số trường hợp đơn giản.",
            "Rút ra được các công thức của chuyển động thẳng biến đổi đều (không được dùng tích phân); vận dụng được các công thức này.",
            "Mô tả và giải thích được chuyển động khi vật có vận tốc không đổi theo một phương và có gia tốc không đổi theo phương vuông góc với phương này.",
            "Thảo luận để thiết kế phương án hoặc lựa chọn phương án và thực hiện phương án, đo được gia tốc rơi tự do bằng dụng cụ thực hành.",
            "Thực hiện được dự án hay đề tài nghiên cứu tìm điều kiện ném vật trong không khí ở độ cao nào đó để đạt độ cao hoặc tầm xa lớn nhất.",
        ]),
    ]),
    ("Cơ học", "Lớp 10", "Động lực học", [
        ("Ba định luật Newton về chuyển động", [
            "Thực hiện thí nghiệm, hoặc sử dụng số liệu cho trước để rút ra được a ~ F, a ~ 1/m, từ đó rút ra được biểu thức a = F/m hoặc F = ma (định luật 2 Newton).",
            "Nêu được khối lượng là đại lượng đặc trưng cho mức quán tính của vật.",
            "Phát biểu định luật 1 Newton và minh hoạ được bằng ví dụ cụ thể.",
            "Vận dụng được mối liên hệ đơn vị dẫn xuất với 7 đơn vị cơ bản của hệ SI.",
            "Nêu được: trọng lực tác dụng lên vật là lực hấp dẫn giữa Trái Đất và vật; trọng tâm của vật là điểm đặt của trọng lực tác dụng vào vật; trọng lượng của vật được tính bằng tích khối lượng của vật với gia tốc rơi tự do.",
            "Phát biểu được định luật 3 Newton, minh hoạ được bằng ví dụ cụ thể; vận dụng được định luật 3 Newton trong một số trường hợp đơn giản.",
        ]),
        ("Một số lực trong thực tiễn", [
            "Mô tả được bằng ví dụ thực tiễn và biểu diễn được bằng hình vẽ: Trọng lực; Lực ma sát; Lực cản khi một vật chuyển động trong nước (hoặc trong không khí); Lực nâng (đẩy lên trên) của nước; Lực căng dây.",
            "Giải thích được lực nâng tác dụng lên một vật ở trong nước (hoặc trong không khí).",
        ]),
        ("Cân bằng lực, moment lực", [
            "Dùng hình vẽ, tổng hợp được các lực trên một mặt phẳng; phân tích được một lực thành các lực thành phần vuông góc.",
            "Nêu được khái niệm moment lực, moment ngẫu lực; nêu được tác dụng của ngẫu lực lên một vật chỉ làm quay vật.",
            "Phát biểu và vận dụng được quy tắc moment cho một số trường hợp đơn giản trong thực tế.",
            "Thảo luận để rút ra được điều kiện để vật cân bằng: lực tổng hợp tác dụng lên vật bằng không và tổng moment lực tác dụng lên vật (đối với một điểm bất kì) bằng không.",
        ]),
        ("Khối lượng riêng, áp suất chất lỏng", [
            "Nêu được khối lượng riêng của một chất là khối lượng của một đơn vị thể tích của chất đó.",
            "Thành lập và vận dụng được phương trình Δp = ρgΔh trong một số trường hợp đơn giản; đề xuất thiết kế được mô hình minh hoạ.",
        ]),
    ]),
    ("Cơ học", "Lớp 10", "Công, năng lượng, công suất", [
        ("Công và năng lượng", [
            "Chế tạo mô hình đơn giản minh hoạ được định luật bảo toàn năng lượng, liên quan đến một số dạng năng lượng khác nhau.",
            "Trình bày được ví dụ chứng tỏ có thể truyền năng lượng từ vật này sang vật khác bằng cách thực hiện công.",
            "Nêu được biểu thức tính công bằng tích của lực tác dụng và độ dịch chuyển theo phương của lực, nêu được đơn vị đo công là đơn vị đo năng lượng (với 1 J = 1 Nm); tính được công trong một số trường hợp đơn giản.",
        ]),
        ("Động năng và thế năng", [
            "Từ phương trình chuyển động thẳng biến đổi đều với vận tốc ban đầu bằng không, rút ra được động năng của vật có giá trị bằng công của lực tác dụng lên vật.",
            "Nêu được công thức tính thế năng trong trường trọng lực đều, vận dụng được trong một số trường hợp đơn giản.",
            "Phân tích được sự chuyển hoá động năng và thế năng của vật trong một số trường hợp đơn giản.",
            "Nêu được khái niệm cơ năng; phát biểu được định luật bảo toàn cơ năng và vận dụng được định luật bảo toàn cơ năng trong một số trường hợp đơn giản.",
        ]),
        ("Công suất và hiệu suất", [
            "Từ một số tình huống thực tế, thảo luận để nêu được ý nghĩa vật lí và định nghĩa công suất.",
            "Vận dụng được mối liên hệ công suất (hay tốc độ thực hiện công) với tích của lực và vận tốc trong một số tình huống thực tế.",
            "Từ tình huống thực tế, thảo luận để nêu được định nghĩa hiệu suất, vận dụng được hiệu suất trong một số trường hợp thực tế.",
        ]),
    ]),
    ("Cơ học", "Lớp 10", "Động lượng", [
        ("Định nghĩa động lượng", [
            "Từ tình huống thực tế, thảo luận để nêu được ý nghĩa vật lí và định nghĩa động lượng.",
        ]),
        ("Bảo toàn động lượng", [
            "Thực hiện thí nghiệm và thảo luận, phát biểu được định luật bảo toàn động lượng trong hệ kín.",
            "Vận dụng được định luật bảo toàn động lượng trong một số trường hợp đơn giản.",
        ]),
        ("Xung lượng và va chạm", [
            "Rút ra được mối liên hệ giữa lực tổng hợp tác dụng lên vật và tốc độ thay đổi của động lượng (lực tổng hợp tác dụng lên vật là tốc độ thay đổi của động lượng của vật).",
            "Thực hiện thí nghiệm và thảo luận được sự thay đổi năng lượng trong một số trường hợp va chạm đơn giản.",
            "Thảo luận để giải thích được một số hiện tượng đơn giản.",
        ]),
    ]),
    ("Cơ học", "Lớp 10", "Chuyển động tròn", [
        ("Động học của chuyển động tròn đều", [
            "Từ tình huống thực tế, thảo luận để nêu được định nghĩa radian và biểu diễn được độ dịch chuyển góc theo radian.",
            "Vận dụng được khái niệm tốc độ góc.",
        ]),
        ("Gia tốc hướng tâm và lực hướng tâm", [
            "Vận dụng được biểu thức gia tốc hướng tâm a = rω², a = v²/r.",
            "Vận dụng được biểu thức lực hướng tâm F = mrω², F = mv²/r.",
            "Thảo luận và đề xuất giải pháp an toàn cho một số tình huống chuyển động tròn trong thực tế.",
        ]),
    ]),
    ("Cơ học", "Lớp 10", "Biến dạng của vật rắn", [
        ("Biến dạng kéo và biến dạng nén; đặc tính của lò xo", [
            "Thực hiện thí nghiệm đơn giản (hoặc sử dụng tài liệu đa phương tiện), nêu được sự biến dạng kéo, biến dạng nén; mô tả được các đặc tính của lò xo: giới hạn đàn hồi, độ dãn, độ cứng.",
        ]),
        ("Định luật Hooke", [
            "Thảo luận để thiết kế phương án hoặc lựa chọn phương án và thực hiện phương án, tìm mối liên hệ giữa lực đàn hồi và độ biến dạng của lò xo, từ đó phát biểu được định luật Hooke.",
            "Vận dụng được định luật Hooke trong một số trường hợp đơn giản.",
        ]),
    ]),
    ("Cơ học", "Lớp 11", "Dao động (Chuyên đề 11.1: Dao động)", [
        ("Dao động điều hoà", [
            "Thực hiện thí nghiệm đơn giản tạo ra được dao động và mô tả được một số ví dụ đơn giản về dao động tự do.",
            "Dùng đồ thị li độ – thời gian có dạng hình sin (tạo ra bằng thí nghiệm, hoặc hình vẽ cho trước), nêu được định nghĩa: biên độ, chu kì, tần số, tần số góc, độ lệch pha.",
            "Vận dụng được các khái niệm: biên độ, chu kì, tần số, tần số góc, độ lệch pha để mô tả dao động điều hoà.",
            "Sử dụng đồ thị, phân tích và thực hiện phép tính cần thiết để xác định được: độ dịch chuyển, vận tốc và gia tốc trong dao động điều hoà.",
            "Vận dụng được các phương trình về li độ và vận tốc, gia tốc của dao động điều hoà.",
            "Vận dụng được phương trình a = –ω²x của dao động điều hoà.",
            "Sử dụng đồ thị, phân tích và thực hiện phép tính cần thiết để mô tả được sự chuyển hoá động năng và thế năng trong dao động điều hoà.",
        ]),
        ("Dao động tắt dần, hiện tượng cộng hưởng", [
            "Nêu được ví dụ thực tế về dao động tắt dần, dao động cưỡng bức và hiện tượng cộng hưởng.",
            "Thảo luận, đánh giá được sự có lợi hay có hại của cộng hưởng trong một số trường hợp cụ thể.",
        ]),
    ]),

    # ---------------- SÓNG HỌC ----------------
    ("Sóng học", "Lớp 11", "Sóng", [
        ("Mô tả sóng", [
            "Từ đồ thị độ dịch chuyển – khoảng cách (tạo ra bằng thí nghiệm, hoặc hình vẽ cho trước), mô tả được sóng qua các khái niệm bước sóng, biên độ, tần số, tốc độ và cường độ sóng.",
            "Từ định nghĩa của vận tốc, tần số và bước sóng, rút ra được biểu thức v = λf; vận dụng được biểu thức này.",
            "Nêu được ví dụ chứng tỏ sóng truyền năng lượng.",
            "Sử dụng mô hình sóng giải thích được một số tính chất đơn giản của âm thanh và ánh sáng.",
            "Thực hiện thí nghiệm (hoặc sử dụng tài liệu đa phương tiện), thảo luận để nêu được mối liên hệ các đại lượng đặc trưng của sóng với các đại lượng đặc trưng cho dao động của phần tử môi trường.",
        ]),
        ("Sóng dọc và sóng ngang", [
            "Quan sát hình ảnh (hoặc tài liệu đa phương tiện) về chuyển động của phần tử môi trường, thảo luận để so sánh được sóng dọc và sóng ngang.",
            "Thảo luận để thiết kế phương án hoặc lựa chọn phương án và thực hiện phương án, đo được tần số của sóng âm bằng dao động kí hoặc dụng cụ thực hành.",
        ]),
        ("Sóng điện từ", [
            "Nêu được trong chân không, tất cả các sóng điện từ đều truyền với cùng tốc độ.",
            "Liệt kê được bậc độ lớn bước sóng của các bức xạ chủ yếu trong thang sóng điện từ.",
        ]),
        ("Giao thoa sóng kết hợp", [
            "Thực hiện (hoặc mô tả) được thí nghiệm chứng minh sự giao thoa hai sóng kết hợp bằng dụng cụ thực hành sử dụng sóng nước (hoặc sóng ánh sáng).",
            "Phân tích, đánh giá kết quả thu được từ thí nghiệm, nêu được các điều kiện cần thiết để quan sát được hệ vân giao thoa.",
            "Vận dụng được biểu thức i = λD/a cho giao thoa ánh sáng qua hai khe hẹp.",
        ]),
        ("Sóng dừng", [
            "Thực hiện thí nghiệm tạo sóng dừng và giải thích được sự hình thành sóng dừng.",
            "Sử dụng hình ảnh (tạo ra bằng thí nghiệm, hoặc hình vẽ cho trước), xác định được nút và bụng của sóng dừng.",
            "Sử dụng các cách biểu diễn đại số và đồ thị để phân tích, xác định được vị trí nút và bụng của sóng dừng.",
        ]),
        ("Đo tốc độ truyền âm", [
            "Thảo luận để thiết kế phương án hoặc lựa chọn phương án và thực hiện phương án, đo được tốc độ truyền âm bằng dụng cụ thực hành.",
        ]),
    ]),
    ("Sóng học", "Lớp 11", "Truyền thông tin bằng sóng vô tuyến (Chuyên đề 11.2)", [
        ("Biến điệu", [
            "So sánh được biến điệu biên độ (AM) và biến điệu tần số (FM).",
            "Liệt kê được tần số và bước sóng được sử dụng trong các kênh truyền thông khác nhau.",
            "Thảo luận để rút ra được ưu, nhược điểm tương đối của kênh AM và kênh FM.",
        ]),
        ("Tín hiệu tương tự và tín hiệu số", [
            "Mô tả được các ưu điểm của việc truyền dữ liệu dưới dạng số so với việc truyền dữ liệu dưới dạng tương tự.",
            "Thảo luận để rút ra được: sự truyền giọng nói hoặc âm nhạc liên quan đến chuyển đổi tương tự – số (ADC) trước khi truyền và chuyển đổi số – tương tự (DAC) khi nhận.",
            "Mô tả được sơ lược hệ thống truyền kĩ thuật số về chuyển đổi tương tự – số và số – tương tự.",
        ]),
        ("Suy giảm tín hiệu", [
            "Thảo luận được ảnh hưởng của sự suy giảm tín hiệu đến chất lượng tín hiệu được truyền; nêu được độ suy giảm tín hiệu tính theo dB và tính theo dB trên một đơn vị độ dài.",
        ]),
    ]),

    # ---------------- NHIỆT HỌC ----------------
    ("Nhiệt học", "Lớp 12", "Vật lí nhiệt", [
        ("Sự chuyển thể", [
            "Sử dụng mô hình động học phân tử, nêu được sơ lược cấu trúc của chất rắn, chất lỏng, chất khí.",
            "Giải thích được sơ lược một số hiện tượng vật lí liên quan đến sự chuyển thể: sự nóng chảy, sự hoá hơi.",
        ]),
        ("Nội năng, định luật 1 của nhiệt động lực học", [
            "Thực hiện thí nghiệm, nêu được: mối liên hệ nội năng của vật với năng lượng của các phân tử tạo nên vật, định luật 1 của nhiệt động lực học.",
            "Vận dụng được định luật 1 của nhiệt động lực học trong một số trường hợp đơn giản.",
        ]),
        ("Thang nhiệt độ, nhiệt kế", [
            "Thảo luận để nêu được sự chênh lệch nhiệt độ giữa hai vật tiếp xúc nhau có thể cho ta biết chiều truyền năng lượng nhiệt giữa chúng; từ đó nêu được khi hai vật tiếp xúc với nhau, ở cùng nhiệt độ, sẽ không có sự truyền năng lượng nhiệt giữa chúng.",
            "Nêu được nhiệt độ không tuyệt đối là nhiệt độ mà tại đó tất cả các chất có động năng chuyển động nhiệt của các phân tử hoặc nguyên tử bằng không và thế năng của chúng là tối thiểu.",
            "Chuyển đổi được nhiệt độ đo theo thang Celsius sang nhiệt độ đo theo thang Kelvin và ngược lại.",
        ]),
        ("Nhiệt dung riêng, nhiệt nóng chảy riêng, nhiệt hoá hơi riêng", [
            "Nêu được định nghĩa nhiệt dung riêng, nhiệt nóng chảy riêng, nhiệt hoá hơi riêng.",
            "Thảo luận để thiết kế phương án hoặc lựa chọn phương án và thực hiện phương án, đo được nhiệt dung riêng, nhiệt nóng chảy riêng, nhiệt hoá hơi riêng bằng dụng cụ thực hành.",
        ]),
    ]),
    ("Nhiệt học", "Lớp 12", "Khí lí tưởng", [
        ("Mô hình động học phân tử chất khí", [
            "Phân tích mô hình chuyển động Brown, nêu được các phân tử trong chất khí chuyển động hỗn loạn.",
            "Từ các kết quả thực nghiệm hoặc mô hình, thảo luận để nêu được các giả thuyết của thuyết động học phân tử chất khí.",
        ]),
        ("Phương trình trạng thái", [
            "Thực hiện thí nghiệm khảo sát được định luật Boyle: Khi giữ không đổi nhiệt độ của một khối lượng khí xác định thì áp suất gây ra bởi khí tỉ lệ nghịch với thể tích của nó.",
            "Thực hiện thí nghiệm minh hoạ được định luật Charles: Khi giữ không đổi áp suất của một khối lượng khí xác định thì thể tích của khí tỉ lệ với nhiệt độ tuyệt đối của nó.",
            "Sử dụng định luật Boyle và định luật Charles rút ra được phương trình trạng thái của khí lí tưởng.",
            "Vận dụng được phương trình trạng thái của khí lí tưởng.",
        ]),
        ("Áp suất khí theo mô hình động học phân tử", [
            "Giải thích được chuyển động của các phân tử ảnh hưởng như thế nào đến áp suất tác dụng lên thành bình và từ đó rút ra được hệ thức p = (1/3)nmv² với n là số phân tử trong một đơn vị thể tích.",
        ]),
        ("Động năng phân tử", [
            "Nêu được biểu thức hằng số Boltzmann, k = R/NA.",
            "So sánh pV = (1/3)Nmv² với pV = nRT, rút ra được động năng tịnh tiến trung bình của phân tử tỉ lệ với nhiệt độ T.",
        ]),
    ]),

    # ---------------- ĐIỆN HỌC ----------------
    ("Điện học", "Lớp 11", "Trường điện (Điện trường)", [
        ("Lực điện tương tác giữa các điện tích", [
            "Thực hiện thí nghiệm hoặc bằng ví dụ thực tế, mô tả được sự hút (hoặc đẩy) của một điện tích vào một điện tích khác.",
            "Phát biểu được định luật Coulomb và nêu được đơn vị đo điện tích.",
            "Sử dụng biểu thức F = q1q2/4πε0r², tính và mô tả được lực tương tác giữa hai điện tích điểm đặt trong chân không (hoặc trong không khí).",
        ]),
        ("Khái niệm điện trường", [
            "Nêu được khái niệm điện trường là trường lực được tạo ra bởi điện tích, là dạng vật chất tồn tại quanh điện tích và truyền tương tác giữa các điện tích.",
            "Sử dụng biểu thức E = Q/4πε0r², tính và mô tả được cường độ điện trường do một điện tích điểm Q đặt trong chân không hoặc trong không khí gây ra tại một điểm cách nó một khoảng r.",
            "Nêu được ý nghĩa của cường độ điện trường và định nghĩa được cường độ điện trường tại một điểm được đo bằng tỉ số giữa lực tác dụng lên một điện tích dương đặt tại điểm đó và độ lớn của điện tích đó.",
            "Dùng dụng cụ tạo ra (hoặc vẽ) được điện phổ trong một số trường hợp đơn giản.",
        ]),
        ("Điện trường đều", [
            "Sử dụng biểu thức E = U/d, tính được cường độ của điện trường đều giữa hai bản phẳng nhiễm điện đặt song song, xác định được lực tác dụng lên điện tích đặt trong điện trường đều.",
            "Thảo luận để mô tả được tác dụng của điện trường đều lên chuyển động của điện tích bay vào điện trường đều theo phương vuông góc với đường sức và nêu được ví dụ về ứng dụng của hiện tượng này.",
        ]),
        ("Điện thế và thế năng điện", [
            "Nêu được điện thế tại một điểm trong điện trường đặc trưng cho điện trường tại điểm đó về thế năng, được xác định bằng công dịch chuyển một đơn vị điện tích dương từ vô cực về điểm đó; thế năng của một điện tích q trong điện trường đặc trưng cho khả năng sinh công của điện trường khi đặt điện tích q tại điểm đang xét.",
            "Vận dụng được mối liên hệ thế năng điện với điện thế, V = A/q; mối liên hệ cường độ điện trường với điện thế.",
        ]),
        ("Tụ điện và điện dung", [
            "Định nghĩa được điện dung và đơn vị đo điện dung (fara).",
            "Vận dụng được (không yêu cầu thiết lập) công thức điện dung của bộ tụ điện ghép nối tiếp, ghép song song.",
            "Thảo luận để xây dựng được biểu thức tính năng lượng tụ điện.",
        ]),
    ]),
    ("Điện học", "Lớp 11", "Dòng điện, mạch điện", [
        ("Cường độ dòng điện", [
            "Thực hiện thí nghiệm (hoặc dựa vào tài liệu đa phương tiện), nêu được cường độ dòng điện đặc trưng cho tác dụng mạnh yếu của dòng điện và được xác định bằng điện lượng chuyển qua tiết diện thẳng của vật dẫn trong một đơn vị thời gian.",
            "Vận dụng được biểu thức I = Snve cho dây dẫn có dòng điện, với n là mật độ hạt mang điện, S là tiết diện thẳng của dây, v là tốc độ dịch chuyển của hạt mang điện tích e.",
            "Định nghĩa được đơn vị đo điện lượng coulomb là lượng điện tích chuyển qua tiết diện thẳng của dây dẫn trong 1 s khi có cường độ dòng điện 1 A chạy qua dây dẫn.",
        ]),
        ("Mạch điện và điện trở", [
            "Định nghĩa được điện trở, đơn vị đo điện trở và nêu được các nguyên nhân chính gây ra điện trở.",
            "Vẽ phác và thảo luận được về đường đặc trưng I – U của vật dẫn kim loại ở nhiệt độ xác định.",
            "Mô tả được sơ lược ảnh hưởng của nhiệt độ lên điện trở của đèn sợi đốt, điện trở nhiệt (thermistor).",
            "Phát biểu được định luật Ohm cho vật dẫn kim loại.",
            "Định nghĩa được suất điện động qua năng lượng dịch chuyển một điện tích đơn vị theo vòng kín.",
            "Mô tả được ảnh hưởng của điện trở trong của nguồn điện lên hiệu điện thế giữa hai cực của nguồn.",
            "So sánh được suất điện động và hiệu điện thế.",
        ]),
        ("Năng lượng điện, công suất điện", [
            "Nêu được năng lượng điện tiêu thụ của đoạn mạch được đo bằng công của lực điện thực hiện khi dịch chuyển các điện tích; công suất tiêu thụ năng lượng điện của một đoạn mạch là năng lượng điện mà đoạn mạch tiêu thụ trong một đơn vị thời gian.",
            "Tính được năng lượng điện và công suất tiêu thụ năng lượng điện của đoạn mạch.",
        ]),
    ]),
    ("Điện học", "Lớp 11", "Mở đầu về điện tử học (Chuyên đề 11.3)", [
        ("Khuếch đại thuật toán", [
            "Thảo luận để nêu được nguyên tắc hoạt động của: điện trở phụ thuộc ánh sáng (LDR), điện trở nhiệt.",
            "Thảo luận để nêu được tính chất cơ bản của bộ khuếch đại thuật toán (op-amp) lí tưởng.",
        ]),
        ("Thiết bị đầu ra", [
            "Thảo luận để nêu được nguyên tắc hoạt động của mạch op-amp – relays; mạch op-amp – LEDs; mạch op-amp – CMs (calibrated meter).",
            "Thiết kế được một số mạch điện ứng dụng đơn giản có sử dụng thiết bị đầu ra.",
        ]),
        ("Thiết bị cảm biến (sensing devices)", [
            "Tham quan thực tế (hoặc qua tài liệu đa phương tiện), thảo luận để nêu được một số ứng dụng chính của thiết bị cảm biến và nguyên tắc hoạt động của thiết bị cảm biến.",
        ]),
    ]),
    ("Điện học", "Lớp 12", "Dòng điện xoay chiều (Chuyên đề 12.1)", [
        ("Các đặc trưng của dòng điện xoay chiều", [
            "Nêu được: công suất toả nhiệt trung bình trên điện trở thuần bằng một nửa công suất cực đại của dòng điện xoay chiều hình sin (chạy qua điện trở thuần này).",
            "Mô tả được bằng biểu thức đại số hoặc đồ thị: cường độ dòng điện, điện áp xoay chiều; so sánh được giá trị hiệu dụng và giá trị cực đại.",
            "Thảo luận để thiết kế phương án hoặc lựa chọn phương án và thực hiện phương án, khảo sát được đoạn mạch xoay chiều RLC mắc nối tiếp bằng dụng cụ thực hành.",
        ]),
        ("Máy biến áp", [
            "Nêu được nguyên tắc hoạt động của máy biến áp.",
            "Nêu được ưu điểm của dòng điện và điện áp xoay chiều trong truyền tải năng lượng điện về phương diện khoa học và kinh tế.",
            "Thảo luận để đánh giá được vai trò của máy biến áp trong việc giảm hao phí năng lượng điện khi truyền dòng điện đi xa.",
        ]),
        ("Chỉnh lưu dòng điện xoay chiều", [
            "Thực hiện thí nghiệm, vẽ được đồ thị biểu diễn quan hệ giữa dòng điện chạy qua diode bán dẫn và điện áp giữa hai cực của nó.",
            "Vẽ được mạch chỉnh lưu nửa chu kì sử dụng diode; vẽ được mạch chỉnh lưu cả chu kì sử dụng cầu chỉnh lưu.",
            "So sánh được đồ thị chỉnh lưu nửa chu kì và chỉnh lưu cả chu kì.",
        ]),
    ]),

    # ---------------- TỪ HỌC ----------------
    ("Từ học", "Lớp 12", "Trường từ (Từ trường)", [
        ("Khái niệm từ trường", [
            "Thực hiện thí nghiệm tạo ra được các đường sức từ bằng các dụng cụ đơn giản.",
            "Nêu được từ trường là trường lực gây ra bởi dòng điện hoặc nam châm, là một dạng của vật chất tồn tại xung quanh dòng điện hoặc nam châm mà biểu hiện cụ thể là sự xuất hiện của lực từ tác dụng lên một dòng điện hay một nam châm đặt trong đó.",
        ]),
        ("Lực từ tác dụng lên đoạn dây dẫn mang dòng điện; Cảm ứng từ", [
            "Thực hiện thí nghiệm để mô tả được hướng của lực từ tác dụng lên đoạn dây dẫn mang dòng điện đặt trong từ trường.",
            "Xác định được độ lớn và hướng của lực từ tác dụng lên đoạn dây dẫn mang dòng điện đặt trong từ trường.",
            "Định nghĩa được cảm ứng từ B và đơn vị tesla; nêu được đơn vị cơ bản và dẫn xuất để đo các đại lượng từ.",
            "Vận dụng được biểu thức tính lực F = BILsinθ.",
        ]),
        ("Từ thông; Cảm ứng điện từ", [
            "Định nghĩa được từ thông và đơn vị weber.",
            "Tiến hành các thí nghiệm đơn giản minh hoạ được hiện tượng cảm ứng điện từ.",
            "Vận dụng được định luật Faraday và định luật Lenz về cảm ứng điện từ.",
            "Giải thích được một số ứng dụng đơn giản của hiện tượng cảm ứng điện từ.",
            "Mô tả được mô hình sóng điện từ và ứng dụng để giải thích sự tạo thành và lan truyền của các sóng điện từ trong thang sóng điện từ.",
        ]),
    ]),

    # ---------------- QUANG HỌC ----------------
    ("Quang học", "Lớp 12", "Vật lí lượng tử – phần quang điện và quang phổ (Chuyên đề 12.3)", [
        ("Hiệu ứng quang điện và năng lượng của photon", [
            "Nêu được tính lượng tử của bức xạ điện từ, năng lượng photon.",
            "Vận dụng được công thức tính năng lượng photon, E = hf.",
            "Nêu được hiệu ứng quang điện là bằng chứng cho tính chất hạt của bức xạ điện từ, giao thoa và nhiễu xạ là bằng chứng cho tính chất sóng của bức xạ điện từ.",
            "Mô tả được khái niệm giới hạn quang điện, công thoát; giải thích được hiệu ứng quang điện dựa trên năng lượng photon và công thoát.",
            "Vận dụng được phương trình Einstein để giải thích các định luật quang điện.",
        ]),
        ("Quang phổ vạch của nguyên tử", [
            "Mô tả được sự tồn tại của các mức năng lượng dừng của nguyên tử.",
            "Giải thích được sự tạo thành vạch quang phổ.",
            "So sánh được quang phổ phát xạ và quang phổ vạch hấp thụ.",
            "Vận dụng được biểu thức chuyển mức năng lượng hf = E1 – E2.",
        ]),
    ]),

    # ---------------- VẬT LÍ HẠT NHÂN ----------------
    ("Vật lí hạt nhân và phóng xạ", "Lớp 12", "Vật lí hạt nhân và phóng xạ", [
        ("Cấu trúc hạt nhân", [
            "Rút ra được sự tồn tại và đánh giá được kích thước của hạt nhân từ phân tích kết quả thí nghiệm tán xạ hạt α.",
            "Biểu diễn được kí hiệu hạt nhân của nguyên tử bằng số nucleon và số proton.",
            "Mô tả được mô hình đơn giản của nguyên tử gồm proton, neutron và electron.",
        ]),
        ("Độ hụt khối và năng lượng liên kết hạt nhân", [
            "Viết được đúng phương trình phân rã hạt nhân đơn giản.",
            "Thảo luận hệ thức E = mc², nêu được liên hệ giữa khối lượng và năng lượng.",
            "Nêu được mối liên hệ giữa năng lượng liên kết riêng và độ bền vững của hạt nhân.",
            "Nêu được sự phân hạch và sự tổng hợp hạt nhân.",
        ]),
        ("Sự phóng xạ và chu kì bán rã", [
            "Nêu được bản chất tự phát và ngẫu nhiên của sự phân rã phóng xạ.",
            "Định nghĩa được độ phóng xạ, hằng số phóng xạ và vận dụng được liên hệ H = λN.",
            "Vận dụng được công thức x = x0e^(–λt), với x là độ phóng xạ, số hạt chưa phân rã hoặc tốc độ số hạt đếm được.",
            "Định nghĩa được chu kì bán rã.",
            "Mô tả được sơ lược một số tính chất của các phóng xạ α, β và γ.",
            "Nêu được các nguyên tắc an toàn phóng xạ; tuân thủ quy tắc an toàn phóng xạ.",
        ]),
    ]),

    # ---------------- VẬT LÍ HIỆN ĐẠI ----------------
    ("Vật lí hiện đại", "Lớp 12", "Vật lí lượng tử (Chuyên đề 12.3)", [
        ("Lưỡng tính sóng hạt", [
            "Mô tả (hoặc giải thích) được tính chất sóng của electron bằng hiện tượng nhiễu xạ electron.",
            "Vận dụng được công thức bước sóng de Broglie: λ = h/p với p là động lượng của hạt.",
        ]),
        ("Vùng năng lượng", [
            "Nêu được các vùng năng lượng trong chất rắn theo mô hình vùng năng lượng đơn giản.",
            "Sử dụng được lí thuyết vùng năng lượng đơn giản để giải thích được: Sự phụ thuộc vào nhiệt độ của điện trở kim loại và bán dẫn không pha tạp; Sự phụ thuộc của điện trở của các điện trở quang (LDR) vào cường độ sáng.",
        ]),
    ]),

    # ---------------- TRÁI ĐẤT VÀ BẦU TRỜI ----------------
    ("Trái Đất và bầu trời", "Lớp 10", "Trái Đất và bầu trời (Chuyên đề 10.2)", [
        ("Xác định phương hướng", [
            "Xác định được trên bản đồ sao (hoặc bằng dụng cụ thực hành) vị trí của các chòm sao: Gấu lớn, Gấu nhỏ, Thiên Hậu.",
            "Xác định được vị trí sao Bắc Cực trên nền trời sao.",
        ]),
        ("Đặc điểm chuyển động nhìn thấy của một số thiên thể trên nền trời sao", [
            "Sử dụng mô hình hệ Mặt Trời, thảo luận để nêu được một số đặc điểm cơ bản của chuyển động nhìn thấy của Mặt Trời, Mặt Trăng, Kim Tinh và Thuỷ Tinh trên nền trời sao.",
            "Dùng mô hình nhật tâm của Copernic giải thích được một số đặc điểm quan sát được của Mặt Trời, Mặt Trăng, Kim Tinh và Thuỷ Tinh trên nền trời sao.",
        ]),
        ("Một số hiện tượng thiên văn", [
            "Dùng ảnh (hoặc tài liệu đa phương tiện), thảo luận để giải thích được một cách sơ lược và định tính các hiện tượng: nhật thực, nguyệt thực, thuỷ triều.",
        ]),
    ]),
]


def seed_taxonomy(db_path=None):
    """Chèn cây taxonomy vào DB nếu chưa có. Idempotent (UNIQUE constraint)."""
    from . import db as dbm

    conn = dbm.get_conn(db_path or dbm.DB_PATH)
    cur = conn.cursor()
    count = {"strand": 0, "content": 0, "unit": 0, "outcome": 0}

    cur.execute("SELECT COUNT(*) c FROM taxonomy_nodes")
    if cur.fetchone()["c"] > 0:
        conn.close()
        return count

    def find_id(level, name, parent_id):
        if parent_id is None:
            cur.execute(
                "SELECT id FROM taxonomy_nodes WHERE level=? AND name=? AND parent_id IS NULL",
                (level, name),
            )
        else:
            cur.execute(
                "SELECT id FROM taxonomy_nodes WHERE level=? AND name=? AND parent_id=?",
                (level, name, parent_id),
            )
        row = cur.fetchone()
        return row["id"] if row else None

    strand_ids = {}
    for s in STRANDS:
        cur.execute(
            "INSERT INTO taxonomy_nodes(level, name, grade, parent_id, source, sort_order) VALUES(1, ?, '', NULL, ?, ?)",
            (s, SOURCE_DEFAULT, len(strand_ids)),
        )
        strand_ids[s] = cur.lastrowid
        count["strand"] += 1

    for strand, grade, content, units in CONTENTS:
        content_id = find_id(2, content, strand_ids[strand])
        if not content_id:
            cur.execute(
                "INSERT INTO taxonomy_nodes(level, name, grade, parent_id, source) VALUES(2, ?, ?, ?, ?)",
                (content, grade, strand_ids[strand], SOURCE_DEFAULT),
            )
            content_id = cur.lastrowid
            count["content"] += 1
        for unit, outcomes in units:
            cur.execute(
                "INSERT INTO taxonomy_nodes(level, name, grade, parent_id, source) VALUES(3, ?, ?, ?, ?)",
                (unit, grade, content_id, SOURCE_DEFAULT),
            )
            unit_id = cur.lastrowid
            count["unit"] += 1
            for yccd in outcomes:
                cur.execute(
                    "INSERT INTO taxonomy_nodes(level, name, grade, parent_id, source) VALUES(4, ?, ?, ?, ?)",
                    (yccd, grade, unit_id, SOURCE_DEFAULT),
                )
                count["outcome"] += 1

    conn.commit()
    conn.close()
    return count