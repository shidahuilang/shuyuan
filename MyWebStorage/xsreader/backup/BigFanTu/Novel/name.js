let fs = require('fs');
// fs.writeFile('./FileName.txt', data, options, callback);
let readDir = fs.readdirSync("./");
let url = "https://fastly.jsdelivr.net/gh/Fantuan-cell/XsRead@main/"
let tag = 'Novel';
url = url +tag;
let name = "";
for (var i = 0; i < readDir.length; i++) {
	name += encodeURI(url+"/"+readDir[i])+"\n"
}

fs.writeFile(`./${tag}FileName.txt`, name, err => {
  if (err) {
    console.error(err)
    return
  }
  //文件写入成功。
})

console.log(name);
// console.log(readDir);