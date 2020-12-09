function addLinkToMarker() {
    var marker_name = document.getElementById('marker_name').value
    var link = document.getElementById('file_link').value
    var placeholder = document.getElementById('marker_placeholder').value
    if (!link) {
        alert('You google drive link is empty. Select one by pressing the icon in the file system view!')
        return
    }
    if (!marker_name) {
        alert('You have to specify name for the marker you wish to add link to!')
        return
    }
    if (!placeholder) {
        alert('You need to specify placeholder name for your google drive link!')
        return
    }
    var desiredItem;
    for (var key in markersData) {
        var item = markersData[key];
        var name = item['id'];
        if (name === marker_name) {
            desiredItem = item
            break;
        }
    }
    if (!desiredItem) {
        alert('Marker with given name was not found. Make sure your name matches the name of one of the listed markers!');
        return
    }
//    console.log(markersData);
    desiredItem['links'][placeholder] = "<a target='_blank' href='" + link + "'>" + placeholder + "</a>";
//    console.log(markersData);
    $.ajax({
          type: "POST",
          contentType: "application/json;charset=utf-8",
          url: "/processMarkers",
          data: JSON.stringify(markersData),
          dataType: "json"
    }).done(function(data) {
//        console.log(data['table']);
        document.getElementById('markersTable').innerHTML = data['table'];
	});
}

function deleteLinkFromMarker() {
    var marker_name = document.getElementById('marker_name').value
    var placeholder = document.getElementById('marker_placeholder').value
    if (!marker_name) {
        alert('You have to specify name for the marker you wish to delete link from!')
        return
    }
    if (!placeholder) {
        alert('You need to specify placeholder name for your google drive link you wish to delete from your marker!')
        return
    }
    itemFound = "no";
    linkFound = "no"
    for (var key in markersData) {
        var item = markersData[key];
        var name = item['id'];
        if (name === marker_name) {
            itemFound = "yes";
            for (var linkName in item['links']){
                if (linkName === placeholder) {
                    linkFound = "yes";
                    delete item['links'][linkName];
                    break
                }
            }
            break;
        }
    }
    if (itemFound === "no"){
        alert("Marker with such name was not found, deletion was not performed!");
        return;
    } else if (linkFound === "no") {
        alert("Such link was not found on the marker and thus could not be deleted!")
        return;
    }
    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/processMarkers",
        data: JSON.stringify(markersData),
        dataType: "json"
    }).done(function(data) {
        document.getElementById('markersTable').innerHTML = data['table'];
	});
}

document.getElementById('add_link').addEventListener("click", addLinkToMarker);
document.getElementById('delete_link').addEventListener("click", deleteLinkFromMarker);
