var productId = Request.QueryString["ID"];
var db = Database.Open("test");
var selectQueryString = string.Format("SELECT * FROM test WHERE ID='{0}'",productId);
var row = db.Query(selectQueryString).First();
<body>
    The selection is 
    <%
        response.write(request.querystring("sex"))
        response.write(" " & request.querystring("age"))
        response.write(" " & request.querystring("type"))
        response.write(" " & request.querystring("keyword"))
    %>
</body>