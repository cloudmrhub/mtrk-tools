var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index.html', { title: 'Generator', section: 'generator', showmenu: 0 });
});

router.get('/inspector', function(req, res, next) {
  res.render('inspector.html', { title: 'Inspector', section: 'inspector', showmenu: 1 });
});

router.get('/settings', function(req, res, next) {
  res.render('settings.html', { title: 'Settings', section: 'settings', showmenu: 0 });
});

module.exports = router;
