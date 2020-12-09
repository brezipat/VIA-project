var data = {name: "Patrik", age: 20, occupation: "dev"};
function fun() {
    console.log(jsonString);
    $.ajax({
          type: "POST",
          contentType: "application/json;charset=utf-8",
          url: "/",
          data: JSON.stringify(data),
          dataType: "json"
          });
}

document.getElementById("but").addEventListener("click", fun);
