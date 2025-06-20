//go:build cgo

package main

/*
#include <stdlib.h>
*/
import "C"

import (
	"fmt"
	"math"
	"unsafe"
)

func solveTransportDualPreference(supply []int, demand []int, cost [][]int) [][]int {
	sl := len(supply)
	dl := len(demand)

	result := make([][]int, sl)
	for i := range result {
		result[i] = make([]int, dl)
	}

	//s := append([]int(nil), supply...)
	//d := append([]int(nil), demand...)

	rowMin := make([]int, sl)
	colMin := make([]int, dl)

	for i := 0; i < sl; i++ {
		rowMin[i] = 0
		for j := 0; j < dl; j++ {
			if i == 0 {
				colMin[j] = 0
			}
			if cost[i][j] < cost[i][rowMin[i]] {
				rowMin[i] = j
			}
			if cost[i][j] < cost[colMin[j]][j] {
				colMin[j] = i
			}
		}
	}

	for i := 0; i < sl; i++ {
		j := rowMin[i]
		if supply[i] > 0 && demand[j] > 0 && colMin[j] == i {
			q := min(supply[i], demand[j])
			result[i][j] = q
			supply[i] -= q
			demand[j] -= q
		}
	}

	for i := 0; i < sl; i++ {
		col := rowMin[i]
		if supply[i] > 0 && demand[col] > 0 && colMin[col] != i {
			q := min(supply[i], demand[col])
			result[i][col] = q
			supply[i] -= q
			demand[col] -= q
		}
	}
	for j := 0; j < dl; j++ {
		row := colMin[j]
		if supply[row] > 0 && demand[j] > 0 && rowMin[row] != j {
			q := min(supply[row], demand[j])
			result[row][j] = q
			supply[row] -= q
			demand[j] -= q
		}
	}

	for {
		minCost := int(^uint(0) >> 1)
		var minI, minJ int
		found := false

		for i := 0; i < sl; i++ {
			if supply[i] == 0 {
				continue
			}
			for j := 0; j < dl; j++ {
				if demand[j] == 0 {
					continue
				}
				if cost[i][j] < minCost {
					minCost = cost[i][j]
					minI = i
					minJ = j
					found = true
				}
			}
		}

		if !found {
			break
		}

		q := min(supply[minI], demand[minJ])
		result[minI][minJ] = q
		supply[minI] -= q
		demand[minJ] -= q
	}

	//print()

	return result
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func BalanceSupplyDemand(supply *[]int, demand *[]int, cost *[][]int) {
	supplySum := 0
	for _, s := range *supply {
		supplySum += s
	}

	demandSum := 0
	for _, d := range *demand {
		demandSum += d
	}

	switch {
	case supplySum < demandSum:
		diff := demandSum - supplySum
		*supply = append(*supply, diff)

		fakeRow := make([]int, len(*demand))
		for i := range fakeRow {
			fakeRow[i] = 0
		}
		*cost = append(*cost, fakeRow)

	case demandSum < supplySum:
		diff := supplySum - demandSum
		*demand = append(*demand, diff)

		for i := range *cost {
			(*cost)[i] = append((*cost)[i], 0)
		}
	}
}

type Point struct {
	I, J int
}

func isValidBasis(plan [][]int) bool {
	m := len(plan)
	n := len(plan[0])

	count := 0
	for i := 0; i < m; i++ {
		for j := 0; j < n; j++ {
			if plan[i][j] > 0 || plan[i][j] == -1 {
				count++
			}
		}
	}
	if count != m+n-1 {
		return false
	}

	for i := 0; i < m; i++ {
		for j := 0; j < n; j++ {
			if plan[i][j] > 0 || plan[i][j] == -1 {
				cycle := buildCycle(plan, i, j)
				if cycle != nil && len(cycle) > 0 {
					return false
				}
			}
		}
	}

	return true
}

func optimizePlanByPotentials(cost [][]int, plan [][]int) {
	m := len(plan)
	n := len(plan[0])

	for {
		u := make([]int, m)
		v := make([]int, n)
		usedU := make([]bool, m)
		usedV := make([]bool, n)

		usedU[0] = true

		updated := true
		for updated {
			updated = false
			for i := 0; i < m; i++ {
				for j := 0; j < n; j++ {
					if plan[i][j] > 0 || plan[i][j] == -1 {
						if usedU[i] && !usedV[j] {
							v[j] = cost[i][j] - u[i]
							usedV[j] = true
							updated = true
						} else if !usedU[i] && usedV[j] {
							u[i] = cost[i][j] - v[j]
							usedU[i] = true
							updated = true
						}
					}
				}
			}
		}

		type cell struct {
			i, j, delta int
		}
		var candidates []cell

		for i := 0; i < m; i++ {
			for j := 0; j < n; j++ {
				if plan[i][j] == 0 {
					delta := cost[i][j] - u[i] - v[j]
					if delta < 0 {
						candidates = append(candidates, cell{i, j, delta})
					}
				}
			}
		}

		if len(candidates) == 0 {
			break
		}

		best := candidates[0]
		for _, c := range candidates {
			if c.delta < best.delta {
				best = c
			}
		}

		i0, j0 := best.i, best.j
		cycle := buildCycle(plan, i0, j0)
		if len(cycle) == 0 {
			fmt.Println("Ошибка: не удалось построить цикл.")
			break
		}

		minVal := math.MaxInt
		for k := 1; k < len(cycle); k += 2 {
			i, j := cycle[k][0], cycle[k][1]
			if plan[i][j] < minVal && plan[i][j] >= 0 {
				minVal = plan[i][j]
			}
		}

		for k := 0; k < len(cycle); k++ {
			i, j := cycle[k][0], cycle[k][1]
			if k%2 == 0 {
				if plan[i][j] == -1 {
					plan[i][j] = minVal
				} else {
					plan[i][j] += minVal
				}
			} else {
				plan[i][j] -= minVal
				if plan[i][j] == 0 {
					plan[i][j] = -1
				}
			}
		}
	}
	for i := 0; i < m; i++ {
		for j := 0; j < n; j++ {
			if plan[i][j] == -1 {
				plan[i][j] = 0
			}
		}
	}
}

func buildCycle(plan [][]int, startI, startJ int) [][2]int {
	m := len(plan)
	n := len(plan[0])

	type point struct{ i, j int }

	basis := make(map[point]bool)
	for i := 0; i < m; i++ {
		for j := 0; j < n; j++ {
			if plan[i][j] > 0 || plan[i][j] == -1 {
				basis[point{i, j}] = true
			}
		}
	}
	basis[point{startI, startJ}] = true

	var cycle [][2]int
	visited := make(map[point]bool)

	var dfs func(curr point, isRow bool) bool
	dfs = func(curr point, isRow bool) bool {
		if curr == (point{startI, startJ}) && len(cycle) >= 4 {
			return true
		}
		if visited[curr] {
			return false
		}
		visited[curr] = true
		cycle = append(cycle, [2]int{curr.i, curr.j})

		if isRow {
			for col := 0; col < n; col++ {
				p := point{curr.i, col}
				if col != curr.j && basis[p] {
					if dfs(p, !isRow) {
						return true
					}
				}
			}
		} else {
			for row := 0; row < m; row++ {
				p := point{row, curr.j}
				if row != curr.i && basis[p] {
					if dfs(p, !isRow) {
						return true
					}
				}
			}
		}

		cycle = cycle[:len(cycle)-1]
		visited[curr] = false
		return false
	}

	if dfs(point{startI, startJ}, true) {
		return cycle
	}
	return nil
}

func solve(supply []int, demand []int, cost [][]int) [][]int {
	BalanceSupplyDemand(&supply, &demand, &cost)
	result := solveTransportDualPreference(supply, demand, cost)
	/*
		length := len(result)
		print("Base plan\n")
		for i := 0; i < length; i++ {
			for j := 0; j < len(result[i]); j++ {
				print(result[i][j], " ")
			}
			print("\n")
		}
		fmt.Printf("valid basis - %t\n", isValidBasis(result))
	*/
	if isValidBasis(result) {
		optimizePlanByPotentials(cost, result)
	}
	return result
}

//export solveTransport
func solveTransport(supplyPtr *C.int, supplyLen C.int, demandPtr *C.int, demandLen C.int, costPtr *C.int, costRows, costCols C.int) *C.int {
	supply := make([]int, int(supplyLen))
	demand := make([]int, int(demandLen))
	cost := make([][]int, int(costRows))

	const maxArraySize = 1 << 26
	supplySlice := (*[maxArraySize]C.int)(unsafe.Pointer(supplyPtr))[:supplyLen:supplyLen]
	demandSlice := (*[maxArraySize]C.int)(unsafe.Pointer(demandPtr))[:demandLen:demandLen]
	costSlice := (*[maxArraySize]C.int)(unsafe.Pointer(costPtr))[: costRows*costCols : costRows*costCols]

	for i := 0; i < int(supplyLen); i++ {
		supply[i] = int(supplySlice[i])
	}
	for i := 0; i < int(demandLen); i++ {
		demand[i] = int(demandSlice[i])
	}
	for i := 0; i < int(costRows); i++ {
		cost[i] = make([]int, int(costCols))
		for j := 0; j < int(costCols); j++ {
			cost[i][j] = int(costSlice[i*int(costCols)+j])
		}
	}

	plan := solve(supply, demand, cost)

	out := (*C.int)(C.malloc(C.size_t(len(supply)*len(demand)) * C.size_t(unsafe.Sizeof(C.int(0)))))
	outSlice := (*[maxArraySize]C.int)(unsafe.Pointer(costPtr))[: costRows*costCols : costRows*costCols]

	for i := 0; i < len(supply); i++ {
		for j := 0; j < len(demand); j++ {
			outSlice[i*len(demand)+j] = C.int(plan[i][j])
		}
	}

	return out
}

//export FreeResult
func FreeResult(ptr *C.int) {
	C.free(unsafe.Pointer(ptr))
}

func main() {
	// Пример использования
	supply := []int{10, 20, 30}
	demand := []int{15, 20, 25}
	cost := [][]int{{5, 3, 1}, {3, 2, 4}, {4, 1, 2}}
	res := solve(supply, demand, cost)
	length := len(res)

	print("Optimized plan\n")
	for i := 0; i < length; i++ {
		for j := 0; j < len(res[i]); j++ {
			print(res[i][j], " ")
		}
		print("\n")
	}

	//cost1 := [][]int{{0, 20, 0}, {9, 0, 36}, {30, 0, 0}, {35, 20, 69}}

	//fmt.Printf("test valid basis - %t\n", isValidBasis(cost1))
	fmt.Print("Done!")

	/*
		supply := []int{20, 30, 25}
		demand := []int{10, 25, 20, 20}
		cost := [][]int{
			{8, 6, 10, 9},
			{9, 7, 4, 2},
			{3, 4, 2, 5},
		}

		result := solveTransportDualPreference(supply, demand, cost)

		fmt.Println("План перевозок:")
		for i := range result {
			fmt.Println(result[i])
		}
	*/
	//fmt.Println("План перевозок:")
}
