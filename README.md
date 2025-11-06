# Ứng dụng Ôn Tập & Ôn Thi

Ứng dụng này là một hệ thống ôn tập trắc nghiệm được xây dựng bằng **Streamlit**. Người dùng có thể tải bộ câu hỏi từ file CSV, tạo đề ngẫu nhiên, chọn đáp án và nhận phản hồi ngay lập tức.

## Tính năng

- **Tạo đề ngẫu nhiên**: Ứng dụng cho phép lấy một bộ câu hỏi ngẫu nhiên từ ngân hàng câu hỏi. Việc lựa chọn ngẫu nhiên sử dụng hàm `random.sample` của Python để đảm bảo mỗi câu hỏi chỉ xuất hiện một lần trong mỗi đề【483697754635941†L25-L33】.
- **Giao diện trực quan**: Mỗi câu hỏi hiển thị ở dạng lựa chọn đơn thông qua `st.radio`, giúp người dùng chọn duy nhất một phương án【838013446759973†L240-L348】.
- **Lưu trạng thái phiên**: Sử dụng `st.session_state` để lưu trữ câu hỏi đã chọn, đáp án người dùng và trạng thái nộp bài. Điều này giúp dữ liệu không bị mất khi ứng dụng được tải lại【878874102014481†L186-L190】.
- **Chấm điểm tự động và hiển thị tham khảo**: Sau khi nộp bài, ứng dụng tự động chấm điểm, thông báo đúng/sai cho từng câu và cung cấp đường dẫn đến văn bản tham chiếu cùng điều khoản cụ thể.

## Cấu trúc thư mục

```
quiz-app/
├── app.py               # Mã nguồn Streamlit
├── questions.csv        # Ngân hàng câu hỏi đã được làm sạch từ file gốc
├── requirements.txt     # Danh sách thư viện cần cài đặt
└── README.md            # Hướng dẫn sử dụng
```

## Chuẩn bị

1. Cài đặt Python 3.8 trở lên.
2. Cài đặt các thư viện cần thiết bằng lệnh:

   ```bash
   pip install -r requirements.txt
   ```

## Chạy ứng dụng

Trong thư mục `quiz-app`, chạy lệnh sau để khởi động ứng dụng Streamlit:

```bash
streamlit run app.py
```

Sau khi chạy, trình duyệt sẽ mở trang web chứa ứng dụng ôn tập. Tại đây bạn có thể:

1. Chọn số lượng câu hỏi muốn ôn.
2. Nhấn **Tạo đề ngẫu nhiên** để sinh ngẫu nhiên bộ câu hỏi.
3. Trả lời từng câu hỏi bằng cách chọn phương án.
4. Nhấn **Nộp bài** để chấm điểm và xem kết quả.
5. Xem tham khảo về văn bản và điều khoản cho từng câu.
6. Nhấn **Làm lại** để bắt đầu một đề mới.

## Chuẩn bị bộ câu hỏi

File `questions.csv` được trích xuất từ dữ liệu gốc và bao gồm các cột:

- `TT`: số thứ tự câu hỏi.
- `Câu hỏi`: nội dung câu hỏi.
- `Phương án A` tới `Phương án E`: các đáp án lựa chọn. Một số câu chỉ có 4 hoặc 5 phương án, phần còn lại để trống.
- `Đ.án đúng`: ký tự A–E chỉ ra đáp án đúng.
- `Số văn bản tham chiếu (kèm trích yếu văn bản)`: tên văn bản liên quan.
- `Điều khoản tham chiếu cụ thể`: điều khoản liên quan trong văn bản.

Nếu bạn muốn cập nhật hoặc thay đổi ngân hàng câu hỏi, hãy chỉnh sửa hoặc thay thế nội dung file `questions.csv` theo đúng định dạng.

## Triển khai lên Streamlit Community Cloud

Để triển khai ứng dụng trên nền tảng **Streamlit Community Cloud**, hãy:

1. Tạo một repository trên GitHub chứa các file trong thư mục `quiz-app`.
2. Đăng nhập vào [Streamlit Community Cloud](https://streamlit.io/cloud) bằng tài khoản GitHub và kết nối tới repository vừa tạo.
3. Chọn `app.py` làm file chính để triển khai ứng dụng.

Ứng dụng sẽ tự động được build và triển khai. Người dùng có thể truy cập đường dẫn do Streamlit cung cấp để ôn tập mọi lúc, mọi nơi.
