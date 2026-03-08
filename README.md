# Time-Lord-I
Description: 
-	Lấy shell bằng cách ghi đè địa chỉ system lên localtime, sau đó nạp vào “/bin/sh\x00”.
-	Để xác định được địa chỉ lệnh thực tế của system thì dựa vào địa chỉ lệnh thực tế của puts (một lệnh đã được chạy) vì khoảng cách của puts và system trong libc không đổi.
-	Tìm địa chỉ puts thực tế bằng cách dùng qword_40A0 đi lùi về số âm. Khi chạy, địa chỉ lệnh được lấy ngẫu nhiên nhưng khoảng cách không thay đổi (giống trong chall: .bss:00000000000040A0 và .got.plt:0000000000004008). Vì 1 qword là 8 byte -> khoảng cách là -19, tính tương tự với localtime được -20.
Địa chỉ base = địa chỉ puts thực tế - địa chỉ puts trong libc.
-	Nạp system vào localtime thông qua ngày tháng năm ở dịch vụ 3.
-	Dùng lỗi Out-of-Bounds (OOB) với Index -1 để ghi đè (làm tràn) biến đếm 255 lần nhằm có vô hạn lượt chơi. Cuối cùng, nạp “/bin/sh\x00” thông qua ngày tháng năm ở dịch vụ 2 và truy c shell bằng dịch vụ 1.
Proof:
<img width="672" height="231" alt="image" src="https://github.com/user-attachments/assets/b10ebb5e-c740-4434-8865-6b1351db0e75" />
<img width="674" height="243" alt="image" src="https://github.com/user-attachments/assets/4a14c3fb-1df5-424f-b93a-4f3c00129f36" />
<img width="684" height="300" alt="image" src="https://github.com/user-attachments/assets/3cfd6386-441f-45c6-97c7-2ebea941edf4" />
<img width="1514" height="916" alt="image" src="https://github.com/user-attachments/assets/87c9ce81-8e7f-4939-a5bb-939a888ca1f9" />
