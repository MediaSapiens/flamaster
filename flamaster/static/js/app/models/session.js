define('models/session', ['backbone'], function(BB) {
  return BB.Model.extend({
    urlRoot: '/account/sessions/',

    is_anonymous: function() {
      console.log(this.toJSON());
    }
  });
});
