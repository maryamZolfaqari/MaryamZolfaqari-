<%@ Language="VBScript" %>

<%
' گرفتن پارامترها از URL
x1 = Request.QueryString("x1")
y1 = Request.QueryString("y1")
x2 = Request.QueryString("x2")
y2 = Request.QueryString("y2")

' اگر همه پارامترها موجود باشند
If x1 <> "" And y1 <> "" And x2 <> "" And y2 <> "" Then

    ' تبدیل به عدد
    x1 = CDbl(x1)
    y1 = CDbl(y1)
    x2 = CDbl(x2)
    y2 = CDbl(y2)

    ' محاسبه فاصله
    dx = x2 - x1
    dy = y2 - y1
    distance = Sqr(dx*dx + dy*dy)

    Response.Write "Point 1: (" & x1 & ", " & y1 & ")<br>"
    Response.Write "Point 2: (" & x2 & ", " & y2 & ")<br>"
    Response.Write "Distance: " & distance & "<br>"

Else
    Response.Write "Use URL like: distance.asp?x1=1&y1=2&x2=4&y2=6"
End If
%>
