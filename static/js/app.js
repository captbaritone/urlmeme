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
var missingLink = document.getElementById('missing-link');
var meme = document.getElementById('meme');
var cancelPending = null;

fields[0].focus();
fields[0].select();

function memeUrl() {
    return fields.map(function (item) {
        var value = item.value || '_';
        return encodeURIComponent(value);
    }).join('/') + '.jpg';
}

function missingLinkHref() {
    var subject = encodeURIComponent("Missing Meme Image");
    var body = encodeURIComponent("I typed '" + fields[0].value + "'" +
        " and expected to get:\n\n" +
        "[[PLEASE ATTACH THE IMAGE YOU EXPECTED TO GET]]." +
        "\n\nThanks!");
    return "mailto:jordan@jordaneldredge.com?" +
        "subject=" + subject + "&body=" + body;
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
    missingLink.setAttribute('href', missingLinkHref());
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
    newImg.src = memeUrl();
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

Rx.Observable.merge(
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