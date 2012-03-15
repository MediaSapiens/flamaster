define('models/user', ['backbone'], function(BB) {
  return BB.Model.extend({
    urlRoot: '/users'
  });
});
