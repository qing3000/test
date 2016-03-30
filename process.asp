<body>
    Welcome
    <%
        response.write(request.querystring("sex"))
        response.write(" " & request.querystring("age"))
        response.write(" " & request.querystring("type"))
        response.write(" " & request.querystring("keyword"))
    %>
</body>