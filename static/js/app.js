// TODO: Don't fade in on initial load
var clipboard = new Clipboard('#copy');
var fields = ['name', 'top', 'bottom'].map(function (item) {
    return document.getElementById(item);
});
var img = document.getElementById('img');
var link = document.getElementById('link');
var hint = document.getElementById('hint');
var copy = document.getElementById('copy');
var cancel = document.getElementById('cancel-copy');
var linkBox = document.getElementById('link-box');
var url = document.getElementById('url');
var meme = document.getElementById('meme');
var missing = document.getElementById('missing');
var cancelPending = null;

fields[0].focus();
fields[0].select();

function memeUrl() {
    return fields.map(function (item) {
        var value = item.value || '_';
        return encodeURIComponent(value);
    }).join('/') + '.jpg';
}

var setDefaultHint = function () {
    hint.innerHTML = '<strong>Give it a try below!</strong>';
}
var cancelCopy = function () {
    linkBox.style.display = "none";
    url.style.display = "block";
    setDefaultHint();
}
copy.addEventListener('click', function (e) {
    linkBox.style.display = "block";
    url.style.display = "none";
    hint.innerHTML = "<strong>Copy!</strong>";
    link.setSelectionRange(0, 9999);
    link.onblur = cancelCopy;
    e.preventDefault();
});

cancel.addEventListener('click', cancelCopy);

setDefaultHint();

fields.forEach(function (item) {
    item.addEventListener('focus', function (e) {
        var hintText = false;
        switch (e.target.id) {
            case 'name':
                hintText = '<strong>Meme name:</strong> A search string that you might type into Google to find this meme.';
                break;
            case 'top':
                hintText = '<strong>Top Text:</strong> The text at the top of your image. Use _ instead of space.';
                break;
            case 'bottom':
                hintText = '<strong>Bottom Text:</strong> The text at the bottom of your image. Use _ instead of space.';
                break;
        }
        hint.innerHTML = hintText;
        this.select();
    });
    item.addEventListener('blur', setDefaultHint);
});

window.addEventListener('resize', function () {
    setMemeHeight(img);
});

function handleChange() {
    fields.forEach(function (item) {
        item.value = item.value.replace(/ /g, "_");
    });
    link.value = baseUrl + memeUrl();
}

function setMemeHeight(newImg) {
    var memeWidth = meme.offsetWidth;
    var imgRatio = newImg.height / newImg.width;
    var newMemeHeight = Math.ceil(memeWidth * imgRatio);
    meme.style.height = newMemeHeight + "px";
}

function getLoadedMemeImg() {
    var newImg = document.createElement('img');
    newImg.classList.add('stale');
    newImg.src = memeUrl() + "?source=www";
    return Rx.Observable.fromEvent(newImg, 'load').mapTo(newImg);
}

function replaceMemeImg(newImg) {
    setMemeHeight(newImg);
    meme.replaceChild(newImg, img);
    img = newImg;
    setTimeout(function () {
        newImg.classList.remove('stale');
    }, 0);
}

const uploadCompetions = new Rx.Subject();

Rx.Observable.merge(
    uploadCompetions,
    Rx.Observable.fromEvent(fields[0], 'input'),
    Rx.Observable.fromEvent(fields[1], 'input'),
    Rx.Observable.fromEvent(fields[2], 'input')
)
    .do(function () {
        img.classList.add('stale');
        handleChange();
    })
    .debounceTime(500)
    .map(memeUrl)
    .switchMap(getLoadedMemeImg)
    .subscribe(replaceMemeImg);

handleChange();
getLoadedMemeImg().subscribe(function (newImg) {
    replaceMemeImg(newImg);
    setTimeout(function () {
        meme.classList.remove('cold')
    }, 0)
});

function uploadFile(file) {
	// Allowed types
	var mime_types = [ 'image/jpeg', 'image/png' ];
	
	// Validate MIME type
	if(mime_types.indexOf(file.type) == -1) {
		alert('Error: Incorrect file type');
		return;
	}

	// Max 2 Mb allowed. This limit is also enforced on the server
	if(file.size > 2*1024*1024) {
		// alert('Error : Exceeded size 2MB');
		// return;
	}

	// Validation is successful
	// This is the name of the file
    // alert('You have chosen the file ' + file.name);
    var data = new FormData();

    var request = new XMLHttpRequest();

    // File selected by the user
    // In case of multiple files append each of them
    data.append('file', file);

    function done() {
        missing.style.background = 'none';
    }

    // AJAX request finished
    request.addEventListener('load', function(e) {
        done();
        if(request.status === 413) { 
            alert("Error uploading image: File too large")
            return;
        } else if(request.status !== 200) { 
            alert("Error uploading image")
            return;
        }
        // request.response will hold the response from the server
        fields[0].value = request.response.meme_name;
        uploadCompetions.next();
    });

    request.addEventListener('error', function(e) {
        done();
        alert("Error: Could not upload image")
    })

    const start = Date.now();

    // Upload progress on request.upload
    request.upload.addEventListener('progress', function(e) {
        var percent_complete = (e.loaded / e.total)*100;
        // If we're on a fast connection, don't bother showing the loading
        if(Date.now() - start > 400) {
            missing.style.background = "linear-gradient(to right, #A1BAA1 " + percent_complete + "%, transparent 0)";
        }
    });

    // If server is sending a JSON response then set JSON response type
    request.responseType = 'json';

    // Send POST request to the server side script
    request.open('post', '/upload'); 
    request.send(data);
}

const upload = document.getElementById('upload')
const uploadButton = document.getElementById('upload-button')
uploadButton.addEventListener('click', function() {
    upload.click();
})
upload.addEventListener('change', function() {
	// This is the file user has chosen
	uploadFile(this.files[0]);
});

let dropArea = document.body;

  
function preventDefaults(e) {
    e.preventDefault()
    e.stopPropagation()
}

function highlight(e) {
    missing.classList.add('dragging')
}

function unhighlight(e) {
    missing.classList.remove('dragging')
}

function handleDrop(e) {
  let dt = e.dataTransfer
  let files = dt.files
  const file = files[0]
  if(file != null) {
    uploadFile(file)
  }
}

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false)
});

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false)
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false)
});

dropArea.addEventListener('drop', handleDrop, false)


