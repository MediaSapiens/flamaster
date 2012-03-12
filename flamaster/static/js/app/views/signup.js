define('views/signup', ['backbone', 'underscore', 'text!templates/signup.html'],
  function(BB, _, template) {
    return BB.View.extend({
      template: _.template(template),

      render: function() {
        return this.$el.html(this.template());
      }
 });
});
