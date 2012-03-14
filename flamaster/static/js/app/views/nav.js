define('views/nav', ['backbone', 'underscore', 'jquery',
  'text!templates/nav.html'],
  function(BB, _, $, template) {

    return BB.View.extend({
      tagName: 'ul',
      className: "nav nav-pills",
      template: _.template(template),

      initialize: function(options) {
        var router = options.router;
        // have to refactor this
        router.on("route:layout", function() {
          this.$el.find("li").removeClass('active');
          this.$el.find(".n-index").addClass('active');
        }, this);

        router.on("route:login", function() {
          this.$el.find("li").removeClass('active');
          this.$el.find(".n-login").addClass('active');
        }, this);

        router.on("route:signup", function() {
          this.$el.find("li").removeClass('active');
          this.$el.find(".n-signup").addClass('active');
        }, this);
      },

      render: function() {
        this.$el.html(this.template({routes: this.model}));
        return this.el;
      }
    });
});
