function init() {
  var tag = $('#selTag').val();
  // Use the list of sample names to populate the select options
  DestroyHideDivsShowLoad()
  GetGraphAndDataFromDB(tag);
}

function ShowAndLoadPlot(x) {
  $('#plot').show()
  $('#plot').append(x);
  $('#loading').hide();
}

function ShowAndLoadData(z) {
  $('#tableData').show()
  $('#tableData').append(z);
  $('#loading2').hide();
}

function DestroyHideDivsShowLoad(){
  $('#plot').html("");
  $('#tableData').html("");
  $('#loading').show();
  $('#plot').hide();
  $('#loading2').show();
  $('#tableData').hide();
}

function GetGraphAndDataFromDB(tag){
  d3.json("/tagplot/" + tag.toString()).then(x =>
    ShowAndLoadPlot(x)
  ).then( y => 
    d3.json("/tag/" + tag.toString()).then(z =>
      ShowAndLoadData(z)
    )
  );
}

function optionChanged(tag) {
  // Fetch new data each time a new tag is selected
  alert("Scraping Twitter for " + tag + "\nThis might take some time...");

  // Use the list of sample names to populate the select options
  DestroyHideDivsShowLoad()
  d3.json("/dowork/" + tag.toString()).then(function(data){ 
    GetGraphAndDataFromDB(tag);
  });
}

$(document).ready(function() {
  // Initialize the dashboard
  init();
  $("#searchTwitter").on("click", function(){
    optionChanged($('#selTag').val());
  })
  $('#searchDatabase').on("click", function(){
    var tag = $('#selTag').val();
    // Use the list of sample names to populate the select options
    DestroyHideDivsShowLoad()
    GetGraphAndDataFromDB(tag);
  });
});

function downloadCSV(csv, filename) {
  var csvFile;
  var downloadLink;

  // CSV file
  csvFile = new Blob([csv], {type: "text/csv"});

  // Download link
  downloadLink = document.createElement("a");

  // File name
  downloadLink.download = filename;

  // Create a link to the file
  downloadLink.href = window.URL.createObjectURL(csvFile);

  // Hide download link
  downloadLink.style.display = "none";

  // Add the link to DOM
  document.body.appendChild(downloadLink);

  // Click download link
  downloadLink.click();
}

function exportTableToCSV(filename) {
  var csv = [];
  var rows = document.querySelectorAll("table tr");
  
  for (var i = 0; i < rows.length; i++) {
      var row = [], cols = rows[i].querySelectorAll("td, th");
      
      for (var j = 0; j < cols.length; j++) 
          row.push(cols[j].innerText);
      
      csv.push(row.join(","));        
  }

  // Download CSV file
  downloadCSV(csv.join("\n"), filename);
}