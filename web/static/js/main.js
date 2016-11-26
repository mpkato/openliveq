var SERP = React.createClass({
  render: function() {
    var changeForm = this.changeForm;
    var questions = this.state.data.map(function (question) {
      return (
        <div className="row" key={question.question_id}>
          <div className="col-xs-8 col-xs-offset-1">
            <ul className="serp">
              <li>
                <Question data={question} />
              </li>
            </ul>
          </div>
          <div className="col-xs-2">
            <QuestionForm data={question} onFormChange={changeForm}/>
          </div>
		</div>
      );
    });
    return (
		<div>{questions}</div>
    );
  },
  loadDataFromServer: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'GET',
      cache: false,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.geturl, status, err.toString());
      }.bind(this)
    });
  },
  changeForm: function(question_id) {
    var submitdata = {evaluations: this.state.data.map(function (question, i) {
        if (question.question_id == question_id)
          question.evaluation = !question.evaluation;
        return {question_id: question.question_id, evaluation: question.evaluation};
    })};
    this.setState({data: this.state.data});
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: JSON.stringify(submitdata),
      contentType: 'application/json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.seturl, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    this.loadDataFromServer();
  }
});

var Question = React.createClass({
  render: function() {
    return (
      <div className="question">
        <label htmlFor={this.props.data.question_id}>
          <div className="title">{this.props.data.title}</div>
        </label>
        <div className="snippet">{this.props.data.snippet}</div>
        <div className="details">
        {this.props.data.status}
        {" "} - 更新日時: {this.props.data.updated_at}
        {" "} - 回答数：{this.props.data.answer_num}
        {" "} - 閲覧数：{this.props.data.view_num}
        </div>
        <div className="category">{this.props.data.category}</div>
      </div>
    );
  }
});

var QuestionForm = React.createClass({
  render: function() {
    var q = this.props.data;
    var classname = q.evaluation ? "form checked" : "form";
    return (
        <label className={classname}>
          <input id={q.question_id}
            type="checkbox"
            checked={q.evaluation}
            onChange={this.changeSelection} />
            <div className="checkboxlabel">
                <span>クリック<br />
                {q.evaluation ? "したい" : "したくない"}</span>
            </div>
        </label>
    );
  },
  changeSelection: function () {
    this.props.onFormChange(this.props.data.question_id);
  },
});

var query_id = $("#meta").data("query");
var order = $("#meta").data("order");
ReactDOM.render(
  <SERP url={"/api/" + query_id + "/" + order} />,
  document.getElementById('content')
);
