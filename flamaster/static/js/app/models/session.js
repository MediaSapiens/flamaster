define('models/session', ['backbone'], function(BB) {
  return BB.Model.extend({
    urlRoot: '/account/sessions/',
    emailRegex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,

    validate: function(attrs) {
      var response = {'status': 'success'};
      if (!this.emailRegex.test(attrs.email)) {
        response.status = 'failed';
        response.email = 'This is not valid email address';
      }
      if (response.status == 'failed') {
        return response;
      }
    },

    is_anonymous: function() {
      console.log(this.toJSON());
    }
  });
});
