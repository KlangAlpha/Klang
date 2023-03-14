/*
 *  
  zigzag = require('./src/zigzag')
  zigzag.peak_valley_pivots([1,2,3,4,5,1,3,4,2,3,1,2,3])
  [
   -1, 0, 0, 0,  1, -1,
    0, 1, 0, 0, -1,  0,
    1
  ]
 *
 *
 */

function peak_valley_pivots(X,step=3){
    var n = X.length;
    if (n < 2){
        return [0]
    }
    pivots = Array.from({length: n}, (item, index) => 0); 


    preindex = 0
    // 获取第一个趋势
    if (X[0] < X[1])
        trend = -1
    else
        trend = 1

    var i = 0;
    for (;i<X.length;i++){
        l = i - step
        r = i + step

        if (l < 0){
            l = 0
        }
        if (l<preindex){
            l  = preindex
        }
        if (r > X.length){
                r = X.length
        }

        x1 = X.slice(l,r)
        if (trend == 1){

            if (X[i] == Math.min(...x1)){
                trend = -1
                pivots[preindex] = 1
                preindex = i
            }
            if (X[i] == Math.max(...x1) && X[i] > X[preindex]){
                preindex = i
            }
        } else {
            if (X[i] == Math.max(...x1)){
                trend = 1
                pivots[preindex] = -1
                preindex = i
            }
            if (X[i] == Math.min(...x1) && X[i] < X[preindex]){
                preindex = i
            }
       }
        // 补充最后一个
       if (trend == 1){
         pivots[preindex] = 1
       } else{
         pivots[preindex] = -1
       }
    }
    return pivots

}

module.exports = {peak_valley_pivots}
