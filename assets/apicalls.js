// Search Photos
function handleSearch(text){
  return sdk.searchGet({
    q: text,
    "x-api-key": "N1FsZYTtIGWKZo73kY7o5o7fl9UZgtlqTqxQFT00",
    "myfirstkey": "N1FsZYTtIGWKZo73kY7o5o7fl9UZgtlqTqxQFT00"}, {}, {})
}
function searchPhotos() {
  const query = document.getElementById('searchQuery').value;
  showResults = document.getElementById("searchResults");
  handleSearch(query)
    .then((response) => {
      // console.log("RESPONSE", response)
      let imglinks = JSON.parse(response["data"]["body"]);
      html = ""
      for (let i=0; i<imglinks.length; i++){
        html+="<img class='photo' src='"
        html+= imglinks[i]
        html += "'/>"
      }
      showResults.innerHTML = html;
    })
    .catch((error) => {
      console.log('Error:', error);
    });
}

function handleUpload(text) {
  var file = document.getElementById("imageInput").files[0];
  file.constructor = () => file;

  sdk.uploadBucketObjectPut({
    bucket: 'b2photostorage',
    'Content-Type': file.type,
    object: file.name,
    'x-amz-meta-customLabels': text
  },
    file, {})
    .then(res => {
      console.log("RES: ", res)
    }).catch((error) => {
      console.log('Error:', error);
    });
}

function uploadPhoto() {
  var text = document.getElementById("uploadInput").value;
  handleUpload(text);
}

// Voice Accessibility
function startVoiceSearch() {
  const recognition = new webkitSpeechRecognition();
  recognition.onresult = function(event) {
      const searchQuery = event.results[0][0].transcript;
      document.getElementById('searchQuery').value = searchQuery;
      searchPhotos();
  }
  recognition.start();
}
