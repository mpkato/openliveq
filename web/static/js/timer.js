var count = 0;
$(function() {
  countDown();
});
function countDown() {
  count += 1;
  $("#time").text(count);
  setTimeout('countDown()', 1000);
};
