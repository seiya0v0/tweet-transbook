/**
function change(id) {
    var text = $("#text"+id).val();
    document.getElementById("trans"+id).innerText = text;
    
}

function check(id) {
    if (document.getElementById("check"+id).checked) {
        document.getElementById("screenshot"+id).style.display = "";
        document.getElementById("trans"+id).style.display = "";
    } else {
        document.getElementById("screenshot"+id).style.display = "none";
        document.getElementById("trans"+id).style.display = "none";
    }
}

function into(id) {
    document.getElementById("screenshot"+id).scrollIntoView()
    document.getElementById("text"+id).scrollIntoView()
}
*/

$("#save-btn").on("click", function() {
    html2canvas(document.getElementById('screenshots'), {useCORS: true}).then(canvas => {
        let saveImg = new Image();
        saveImg.setAttribute('crossOrigin', '');
        saveImg.src = canvas.toDataURL();  // 导出图片
        document.getElementById("save-img").appendChild(saveImg);  // 将生成的图片添加到body      
        $("#img-show").fadeIn("fast");
    });
});

$("#img-show").on("click", function() {
    $(this).fadeOut("fast");
    $("#save-img").innerHTML = "";
});

$("#template-btn").on("click", function() {
    if ($("#translatetemp").css("display") == "none") {
        $("#translatetemp").show();
    } else {
        $("#translatetemp").hide();
    }
});



function run() {
    url = $("#url").val();
    url = url.replace("http:", "https:");
    url = url.replace("mobile.twitter.com", "twitter.com");
    url = url.replace(/\?.*/, "");
    $("#url").val(url);
    $('#progress').val("开始获取推文（这可能需要几分钟的时间）");
    $('#url').css("display", "none");
    $('#progress').css("display", "");
    $('#button-submit').attr("disabled", "disabled");
    $.ajax({
        type: 'POST',
        url: "/api",
        data: url,
        dataType: "json",
        success: function(data) {
            if (data["code"] == 200) {
                $('#progress').val("完成！正在加载数据");
                $("#sample-tab").remove()
                $('#sample-sc').remove()
                load(data["data"]);
                $('#progress').val("加载完成");
            } 
            else if (data["code"] == 0) {
                $("#url").val("获取失败, 请检查网络链接");
                $('#url').css("display", "");
                $('#progress').css("display", "none");
                $('#button-submit').removeAttr("disabled");
            }
        }, 
        error: function(xhr, type) {
            $("#url").val("链接不可用, 请确认后重新输入");
            $('#url').css("display", "");
            $('#progress').css("display", "none");
            $('#button-submit').removeAttr("disabled");
        }
    });
}

function load(data) {
    data.forEach(element => {
        loadImg(element["img"], element["index"]);
        loadTrans(element["text"], element["index"]);
    });

    $(".sc-box").on("click", function() {
        var id = this.id.replace("sc", "");
        $("#text"+id)[0].scrollIntoView();
    });
    
    $(".index").on("click", function() {
        var id = this.textContent;
        $("#sc"+id)[0].scrollIntoView();
    });

    $(".form-control").on("input", function() {
        var id = this.id.replace("text", "");
        var temple = $("#translatetemp").val();
        var text = $(this).val();
        if (text == "") {
            temple = "";
        }
        $("#trans"+id)[0].innerHTML = temple + text;
    });

    $(".switch").on("change", function() {
        var id = this.id.replace("check", "");
        if (this.checked) {
            $("#sc"+id).css("display", "");
        } else {
            $("#sc"+id).css("display", "none");
        }
    });
}

function loadImg(img, index) {
    if (index.slice(-1) == "1") {
        if (index != "1-1") {
            $("#screenshots").append(`<HR class="line">`)
        }
    }
    var sc_html = `
    <div id="sc${index}" class="sc-box">
        <img src="${img}"/>
        <div class="trans-box" id="trans${index}"></div>
    </div>`;
    $("#screenshots").append(sc_html)
    if (index == "1-1") {
        $("#trans1-1").css("margin-left", "16px");
    }
}

function loadTrans(text, index) {
    var trans_html = `
    <tr>
        <th scope="row">
            <p class="index">${index}</p>
            <input type="checkbox" id="check${index}" class="switch" checked>
        </th>
        <td class="originaltext">${text}</td>
        <td>
            <div class="translatetd">
                <div class="input-group">
                    <textarea id="text${index}" class="form-control"></textarea>
                </div>
            </div>
        </td>
    </tr>
    `
    $("#translatetbody").append(trans_html)
}