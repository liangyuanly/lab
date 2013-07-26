import matplotlib

def TagTokenPlot(filename):
    tag_tokens = json.load(filename);

    for tag, token_seq in tag_tokens.iteritems():
        x = [];
        y = [];
        count = 1;
        for token, freq in sorted(token_seq.iteritems(), key=lambda (k,v):(v,k)):
            x.append(count);
            count = count + 1;
            y.append(freq);
        plt.hist(x, y);
